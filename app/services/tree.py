from sqlalchemy.orm import Session
from app.models.models import User, Referral, App
from typing import Dict, List, Any

class TreeService:
    @staticmethod
    def get_referral_tree(db: Session, app_id: int):
        app = db.query(App).filter(App.id == app_id).first()
        if not app:
            return None

        # Get all users for this app
        users = db.query(User).filter(User.app_id == app_id).all()
        
        # Build a lookup for quick access
        user_lookup = {user.id: user for user in users}
        
        # Find all referral links
        referrals = db.query(Referral).filter(Referral.app_id == app_id).all()
        
        # Build child maps
        children_map = {}
        referees = set()
        for ref in referrals:
            if ref.referrer_id not in children_map:
                children_map[ref.referrer_id] = []
            children_map[ref.referrer_id].append(ref.referee_id)
            referees.add(ref.referee_id)

        # Roots are users who were NOT referred by anyone but HAVE referred others
        # Actually roots are anyone not in 'referees' set
        root_nodes = [user for user in users if user.id not in referees]

        def build_node(user_id):
            user = user_lookup[user_id]
            node = {
                "external_user_id": user.external_user_id,
                "referral_code": user.referral_code,
                "children": []
            }
            if user_id in children_map:
                for child_id in children_map[user_id]:
                    node["children"].append(build_node(child_id))
            return node

        repo_tree = [build_node(root.id) for root in root_nodes]
        
        return {
            "app_name": app.name,
            "root_users": repo_tree
        }
