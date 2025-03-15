from fastapi import Request, Response, FastAPI
from strictyaml import load
import threading
import logging
import hmac
import hashlib
import printer
import imggen
import base64
import json
import uvicorn

with open("config.yaml", "r") as f:
    config = load(f.read()).data

logger = logging.getLogger('uvicorn.error')
lock = threading.Lock()

printer.init_printer(bytes.fromhex(config['printer']['maj']), bytes.fromhex(config['printer']['min']))

app = FastAPI()

group = 1
serial = 1

def verify_message(message: bytes, signature: bytes):
    h = hmac.new(config['tito']['mac_token'].encode('utf-8'), message, hashlib.sha256).digest()
    return hmac.compare_digest(h, signature)

@app.post("/")
async def create_checkin(request: Request):
    body = await request.body()
    signature = request.headers.get("Tito-Signature")
    if signature is None:
        logger.warning("Rejecting message with missing signature")
        return Response(status_code=403)

    if not verify_message(body, base64.b64decode(signature)):
        logger.warning("Rejecting unauthenticated message")
        return Response(status_code=403)

    lock.acquire(True)
    
    try:
        global group
        global serial
        
        content = json.loads(body.decode('utf-8'))
        attendee_name = content['name']
        ticket_type = content['release_title']
        ticket_ref = content['reference']
        slug = content['slug']
        pronouns = list(filter(lambda a: a['question'] == 'What are your preferred pronouns?', content['answers']))[0]['response']
        logger.info(f"Printing attendee pass for {attendee_name}...")
        printer.print_pass(imggen.name(attendee_name), imggen.pronouns(pronouns), ticket_ref, ticket_type, slug)

        pizza_pref = list(filter(lambda a: a['question'] == 'What is your pizza preference?', content['answers']))
        if len(pizza_pref) == 0:
            return "ok"

        d_reqs = list(filter(lambda a: a['question'] == 'Do you have any dietary restrictions?', content['answers']))
        logger.info(f"Printing food token for {attendee_name}...")
        if len(d_reqs) == 0:
            printer.print_food(attendee_name, pizza_pref[0]['response'], str(group), None)
        else:
            printer.print_food(attendee_name, pizza_pref[0]['response'], str(group), d_reqs[0]['response'])

        serial = serial + 1
        if serial % 10 == 0:
            group = group + 1
            logger.info(f"Incrementing group counter to {group}")

        return Response(status_code=204)
    finally:
        lock.release()

    
if __name__ == '__main__':
    uvicorn.run(app, log_level="info", host="0.0.0.0", port=3000)

