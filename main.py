from datetime import datetime
from http.client import HTTPException

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, RequestValidationError
from fastapi.responses import JSONResponse
import fastapi.openapi.utils as fu
from pydantic import BaseModel
import csv, re, logging

logging.basicConfig(filename='logs/{:%Y-%m-%d}.log'.format(datetime.now()), filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
app = FastAPI()

# and override the schema
fu.validation_error_response_definition = {
    "title": "HTTPValidationError",
    "type": "object",
    "properties": {
        "error": {"title": "Message", "type": "string"}, 
    },
}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"confirm": False, "signature": False, "msg": "Request error"}),
    )

csvdata  = {}

with open('binlist.csv', encoding="utf8") as csvfile :
    headers = csvfile.readline().split(";")[1:]
    headers = ["recipient", "system", "currency"]
    csvrows = csv.reader(csvfile, delimiter=";")
    for row in csvrows:
        csvdata[row[0]] = {k:v  for k, v in zip(headers, row[1:])}

def lunh(cardNo):
    nDigits = len(cardNo)
    if (nDigits < 16):
        logging.warning('cardNo %s not found', cardNo)
        return False
    nSum = 0
    isSecond = False
    for i in range(nDigits - 1, -1, -1):
        d = ord(cardNo[i]) - ord('0')
        if (isSecond == True):
            d = d * 2
        nSum += d // 10
        nSum += d % 10
        isSecond = not isSecond
    if (nSum % 10 == 0):
        return True ## Card Passed Check
    else:
        return False ## Card Failed Check

class Card(BaseModel):
    iin: int | None = None
    recipient: str | None = None
    system: str | None = None
    currency: str | None = None

class Lookup(BaseModel):
    verify: bool | None = None
    card: Card | None = None

class Payment(BaseModel):
    pan: int
    expire: int
    pan2: int
    amount: int
    ccy_code: int
    merchant_id: str | None = None
    terminal_id: str | None = None
    recipient_name: str
    tax_id_no: str | None = None
    client_name: str
    client_address: str
    client_city: str
    get_available_amount: int | None = None

class Validation(BaseModel):
    confirm: bool
    signature: bool
    msg: str | None = None

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/lookup/{card}", response_model=Lookup)
async def lookup(card):
    if not card:
        raise HTTPException(status_code=404, detail="Card field is required")
    res = {"verify": None, "card": None}
    iin = re.sub("\s", "", card)
    iin = iin[0:6]
    res["verify"] = lunh(card)
    if (iin in csvdata):
        res["card"] = {"iin": int(iin)}
        res["card"].update(csvdata[iin])
    else:
        logging.warning('iin %s not found', iin)
    return res

@app.post("/confirm", response_model=Validation)
async def confirm(payment: Payment):
    logging.warning('%s', payment)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment fields not found")
    panCheck = lunh(str(payment.pan2))
    return {"confirm": True, "signature": True, "msg": ""}
