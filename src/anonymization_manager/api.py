"""
REST API for the AnonymizationManager.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from .core import AnonymizationManager
from .config import AnonymizationConfig

app = FastAPI()

@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request: Request, ex: FileNotFoundError):
    """
    Handles file-related errors raised during configuration validation.

    Args:
        request (Request): The incoming request that triggered the error.
        ex (FileNotFoundError): The raised exception.
    
        Returns:
            JSONResponse: A 400 response containing the error message.
    """
    return JSONResponse(status_code=400, content={"detail":str(ex)})

@app.exception_handler(RequestValidationError)
async def validation_fail_handler(request: Request, ex: Exception):
    """
    Anonymizes a dataset according to the provided configuration.

    Args:
        config (AnonymizationConfig): The anonymization configuration.
    
    Re
    """
    messages = [err["msg"] for err in ex.errors()]
    return JSONResponse(status_code=400, content={"detail":messages})

@app.post("/anonymize")
def anonymize(config: AnonymizationConfig):
    """
    Anonymizes a dataset according to the provided configuration.

    Args:
        config (AnonymizationConfig): The anonymization configuration.
    
    Returns:
        JSONResponse: A 200 response containing:
            - data: the anonymized dataset as a list of JSON records.
            - metadata: statistics describing the transformation, including the
              anonymization time.
    """
    try:
        result = AnonymizationManager.anonymize(config)
        content={
            "data": result.get_anonymized_data_as_dataframe().to_dict(orient="records"),
            "metadata": {
                "anonymization_time_ms" : result.get_anonymization_time(),
                "average_equivalence_class_size" : result.get_average_equivalence_class_size(),
                "transformations" : result.get_transformations()
            }                      
        }
        return JSONResponse(content=jsonable_encoder(content))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occured: {str(e)}")