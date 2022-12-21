from datetime import datetime
from http.client import HTTPException
import json
import string

from fastapi import FastAPI, Request, status, APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, RequestValidationError
from fastapi.responses import JSONResponse
import fastapi.openapi.utils as fu
from pydantic import BaseModel
import csv, re, logging, sys, time
import aiomysql, asyncio

loop = asyncio.get_event_loop()
logging.basicConfig(filename='/code/logs/{:%Y-%m-%d}.log'.format(datetime.now()), filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
app = FastAPI()
api_router = APIRouter()

# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     response = await call_next(request)
#     request_body = await request.json()

#     logging.info(
#         f"{request.method} request to {request.url} metadata\n"
#         f"\tHeaders: {request.headers}\n"
#         f"\tBody: {request_body}\n"
#         f"\tPath Params: {request.path_params}\n"
#         f"\tQuery Params: {request.query_params}\n"
#         f"\tCookies: {request.cookies}\n"
#     )
    
#     return response


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

with open('/code/binlist.csv', encoding="utf8") as csvfile :
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

async def aml(name):
    conn = await aiomysql.connect(host="195.158.1.135", port=3306, user="root", password="V1ZkNGRtTlhSbWxaVnpWeQ==", db="validation-service")
    cur = await conn.cursor()

    sql = "SELECT * FROM blacklist WHERE name = \"%s\"" % (name)
    print(name)
    
    await cur.execute(sql)
    r = await cur.fetchall()
    return bool(r)

async def banlist(pan):
    conn = await aiomysql.connect(host="195.158.1.135", port=3306, user="root", password="V1ZkNGRtTlhSbWxaVnpWeQ==", db="validation-service")
    cur = await conn.cursor()

    sql = "SELECT * FROM blacklist_pan WHERE pan = %d" % (pan)
    
    await cur.execute(sql)
    r = await cur.fetchall()
    return bool(r)

async def whitelist(pan):
    conn = await aiomysql.connect(host="195.158.1.135", port=3306, user="root", password="V1ZkNGRtTlhSbWxaVnpWeQ==", db="validation-service")
    cur = await conn.cursor()

    sql = "SELECT * FROM whitelist WHERE pan = %d" % (pan)
    
    await cur.execute(sql)
    r = await cur.fetchall()
    return bool(r)

class Card(BaseModel):
    iin: int | None = None
    recipient: str | None = None
    system: str | None = None
    #currency: str | None = None
class Lookup(BaseModel):
    verify: bool | None = None
    card: Card | None = None
class Payment(BaseModel):
    pan: int
    recipient_name: str
class Validation(BaseModel):
    confirm: bool
    signature: bool
    code: int

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/lookup/{card}", response_model=Lookup)
async def lookup(card):
    sql = "INSERT INTO requests (datetime, request, endpoint) VALUES (NOW(), \"%s\", \"%s\")" % (card, "/lookup")
    print(sql)
    conn = await aiomysql.connect(host="195.158.1.135", port=3306, user="root", password="V1ZkNGRtTlhSbWxaVnpWeQ==", db="validation-service")
    cur = await conn.cursor()
    await cur.execute(sql)
    await conn.commit()
    
    if not card:
        raise HTTPException(status_code=404, detail="Card field is required")
    res = {"verify": None, "card": None}
    iin = re.sub("\s", "", card)
    iin = iin[0:6]
    res["verify"] = lunh(card)
    if (iin in csvdata):
        res["card"] = {"iin": int(iin)}
        res["card"].update(csvdata[iin])
        print(card[0:9])
        if (card[0:9] == '419525008'):
            res["card"]["currency"] = "UZS"
    else:
        logging.warning('iin %s not found', iin)
    return res

@app.post("/confirm", response_model=Validation)
async def confirm(payment: Payment):
    sql = "INSERT INTO requests (datetime, request, endpoint) VALUES (NOW(), %s, \"%s\")" % (json.dumps(payment.json()), "/confirm")
    print(sql)
    conn = await aiomysql.connect(host="195.158.1.135", port=3306, user="root", password="V1ZkNGRtTlhSbWxaVnpWeQ==", db="validation-service")
    cur = await conn.cursor()
    await cur.execute(sql)
    await conn.commit()
    _confirm = True
    _code = 0

    aml_check = await aml(payment.recipient_name)
    print(aml_check)
    pan_check = await banlist(payment.pan)
    print(pan_check)
    ignore = await whitelist(payment.pan)
    print(ignore)
    _confirm = ignore or (not pan_check and not aml_check)

    if (pan_check):
        _code = 12
    if (aml_check):
        _code = 11
    if (aml_check and pan_check):
        _code = 10

    logging.warning('%s', payment)
    if not payment:
        raise HTTPException(status_code = 404, detail = "Payment fields not found")
    panCheck = lunh(str(payment.pan))
    return {"confirm": _confirm, "signature": True, "code": _code}
