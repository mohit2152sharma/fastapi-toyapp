import logging
import random
from datetime import timedelta
from typing import Annotated, Dict

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt

from .models import Token, TokenData, User, get_user
from .security import (access_token_expire_time, algorithm, authenticate_user,
                       create_access_token, oauth2_scheme, secret_key)
from .utils import read_db

app = FastAPI()
logging.basicConfig(level=logging.INFO)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme())]) -> User:
    """checks if the current user is a valid user or not. If not raises an exception

    Args:
        token: token to authenticate user

    Returns:
        User, if it is a valid user otherwise exception
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key(), algorithms=[algorithm()])
        username: str = payload.get("sub")  # type: ignore
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    db = read_db()
    user = get_user(db, username=token_data.username)  # type: ignore
    if user is None:
        raise credentials_exception
    return user


@app.get("/array")
async def read_sentence(
    current_user: Annotated[User, Depends(get_current_user)],
    sentence: str,
    n: int = 500,
) -> Dict:
    """Reads the sentence passed by user and returns an array with additional information

    Args:
        current_user: user information required for authentication
        sentence: sentence passed by user
        n: length of array (Defaults to 500)

    Returns:
        A Dictionary with user information and array
    """
    logging.info(f"The sentence passed by user: {sentence}")

    # it might be expected to use numpy.random.rand() here
    # but I preferred to not use it as it introduces an
    # external package dependency `numpy`. Also numpy is a big
    # package and it increases the overall size of image/package
    # for this simple use-case `random()` package from built-in
    # library is enough
    array = [round(random.uniform(0, 5), 2) for _ in range(n)]
    response = {
        "user": {
            "username": current_user.username,
            "display_name": current_user.display_name,
            "emailid": current_user.email,
        },
        "array": array,
    }
    return response


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Dict:
    """authenticates the user and returns a token

    Args:
        form_data: form data with username and password

    Raises:
        HTTPException: Raises an exception if the user is not a valid user

    Returns:
        token and token type
    """
    db = read_db()
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=access_token_expire_time())
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
