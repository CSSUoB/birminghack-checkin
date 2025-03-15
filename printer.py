from PIL import Image
from escpos.printer import Usb
from typing import Optional, Union
import logging

logger = logging.getLogger(__name__)
p = Usb(0x1fc9,0x2016,0,profile="TM-P80")

def print_pass(name_image: Union[str, Image.Image], pronouns_image: Union[str, Image.Image], reference: str, ticket_type: str, slug: str):
    logger.info(f"Printing pass for {ticket_type}")
    p.linedisplay_clear()
    p.image("birminghack-logo-raster-bw-rs.png",center=True)
    p.ln()
    p.ln()
    p.image(name_image,center=True)
    p.image(pronouns_image,center=True)
    p.set(align="left",bold=False,custom_size=True,width=2,height=2)
    p.ln()
    p.qr(slug, size=10, center=True)
    p.set(align="left",bold=True,normal_textsize=True)
    p.software_columns(["Reference", reference], widths=48, align=["left", "right"])
    p.software_columns(["Type", ticket_type], widths=48, align=["left", "right"])
    p.set(align="left",bold=False,normal_textsize=True)
    p.ln()
    p.textln("By attending this event you agree to the")
    p.textln("birmingHack Code of Conduct:")
    p.set(align="right",bold=False,normal_textsize=True)
    p.textln("birminghack.com/conduct")
    p.set(align="left",bold=False,normal_textsize=True)
    p.ln()
    p.textln("Please wear your attendee pass at all times.")
    p.cut()

def print_food(issued_to: str, pizza_type: str, group: str, d_req: Optional[str] = None):
    logger.info(f"Printing pizza token for {issued_to}")
    p.linedisplay_clear()
    p.ln()
    p.set(align="center",bold=True,custom_size=True,width=3,height=3,smooth=True)
    p.textln("Pizza Token")
    p.ln()
    p.set(align="left",bold=False,normal_textsize=True)
    p.textln("Exchange me for pizza!")
    p.image("pizza.png",center=True)
    p.ln()
    p.set(align="left",bold=True,normal_textsize=True)
    p.software_columns(["Group", group], widths=48, align=["left", "right"])
    p.software_columns(["Pizza Type", pizza_type], widths=48, align=["left", "right"])
    p.software_columns(["Issued To", issued_to], widths=48, align=["left", "right"])
    p.ln()
    if d_req:
        p.set(align="left",bold=False,custom_size=True,width=2,height=2,invert=True)
        p.textln("Dietary Requirement")
        p.ln()
        p.set(align="left",bold=False,normal_textsize=True,invert=False)
        p.textln(d_req)
    p.cut()

