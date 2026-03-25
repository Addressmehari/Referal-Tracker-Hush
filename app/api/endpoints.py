from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import App, User, Referral
from app.schemas.schemas import AppCreate, AppResponse, UserCreate, UserResponse, TrackReferral
from app.services.tree import TreeService
import secrets
import string

router = APIRouter()

# Helper to verify API Key
async def verify_api_key(api_key: str = Header(None, alias="X-API-KEY"), db: Session = Depends(get_db)):
    if not api_key:
        raise HTTPException(status_code=401, detail="API Key missing")
    app_obj = db.query(App).filter(App.api_key == api_key).first()
    if not app_obj:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return app_obj

# --- API Endpoints ---

# 1. Register or List Apps (Developer Level)
@router.post("/apps", response_model=AppResponse)
def create_app(app_in: AppCreate, db: Session = Depends(get_db)):
    app_obj = App(name=app_in.name)
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    return app_obj

@router.get("/apps", response_model=list[AppResponse])
def list_apps(db: Session = Depends(get_db)):
    return db.query(App).all()

# 2. Generate a Referral Code for a User
@router.post("/users/generate-code", response_model=UserResponse)
def generate_code(user_in: UserCreate, 
                 developer_app: App = Depends(verify_api_key), 
                 db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        User.app_id == developer_app.id, 
        User.external_user_id == user_in.external_user_id
    ).first()
    
    if existing_user:
        return existing_user

    code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    new_user = User(
        app_id=developer_app.id,
        external_user_id=user_in.external_user_id,
        referral_code=code
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 3. Track a Referral Action
@router.post("/referrals/track")
def track_referral(track_in: TrackReferral, 
                  developer_app: App = Depends(verify_api_key), 
                  db: Session = Depends(get_db)):
    
    referrer = db.query(User).filter(
        User.app_id == developer_app.id,
        User.referral_code == track_in.referral_code
    ).first()
    
    if not referrer:
        raise HTTPException(status_code=404, detail="Referral code not found")

    existing_referee = db.query(User).filter(
        User.app_id == developer_app.id,
        User.external_user_id == track_in.referee_id
    ).first()
    
    if existing_referee:
        is_already_referred = db.query(Referral).filter(Referral.referee_id == existing_referee.id).first()
        if is_already_referred:
              return {"message": "Referee already tracked"}
        referee = existing_referee
    else:
        new_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        referee = User(
            app_id=developer_app.id,
            external_user_id=track_in.referee_id,
            referral_code=new_code
        )
        db.add(referee)
        db.flush()

    new_referral = Referral(
        app_id=developer_app.id,
        referrer_id=referrer.id,
        referee_id=referee.id,
        code_used=track_in.referral_code
    )
    db.add(new_referral)
    db.commit()
    
    return {"status": "success", "message": f"{track_in.referee_id} linked to {referrer.external_user_id}"}

# 4. Get the Tree Visualization Data
@router.get("/apps/{app_id}/tree")
def get_tree(app_id: int, db: Session = Depends(get_db)):
    tree = TreeService.get_referral_tree(db, app_id)
    if not tree:
        raise HTTPException(status_code=404, detail="App not found")
    return tree
