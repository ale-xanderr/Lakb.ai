from typing import Optional, Dict, Any
from supabase import Client
from core.supabase_client import get_supabase_client
import os


class ProfileService:
    def __init__(self):
        self.client: Client = get_supabase_client()
        self.bucket_name = "avatars"

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch user profile data from Supabase profiles table.
        Returns profile data or None if not found.
        """
        if not self.client:
            return None
        
        try:
            response = self.client.table('profiles').select('*').eq('id', user_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return None

    def create_user_profile(self, user_id: str, email: str, first_name: str = "", last_name: str = "") -> bool:
        """
        Create a new user profile in the profiles table.
        Returns True if successful, False otherwise.
        """
        if not self.client:
            return False
        
        try:
            data = {
                'id': user_id,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            }
            response = self.client.table('profiles').insert(data).execute()
            return True
        except Exception as e:
            print(f"Error creating user profile: {e}")
            return False

    def update_user_profile(self, user_id: str, first_name: Optional[str] = None, 
                          last_name: Optional[str] = None, email: Optional[str] = None) -> bool:
        """
        Update user profile information in Supabase.
        Returns True if successful, False otherwise.
        """
        if not self.client:
            return False
        
        try:
            # Build update data
            update_data = {}
            if first_name is not None:
                update_data['first_name'] = first_name
            if last_name is not None:
                update_data['last_name'] = last_name
            if email is not None:
                update_data['email'] = email
            
            if not update_data:
                return True  # Nothing to update
            
            # Update profile table
            response = self.client.table('profiles').update(update_data).eq('id', user_id).execute()
            
            # If email is being updated, also update auth.users email
            if email is not None:
                try:
                    self.client.auth.update_user({'email': email})
                except Exception as e:
                    print(f"Warning: Could not update auth email: {e}")
            
            return True
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False

    def update_password(self, new_password: str) -> tuple[bool, str]:
        """
        Update user password via Supabase Auth.
        Returns (success, message) tuple.
        """
        if not self.client:
            return False, "Supabase client not initialized"
        
        try:
            response = self.client.auth.update_user({'password': new_password})
            if response:
                return True, "Password updated successfully"
            return False, "Failed to update password"
        except Exception as e:
            error_msg = str(e)
            print(f"Error updating password: {error_msg}")
            return False, f"Error: {error_msg}"

    def upload_profile_image(self, user_id: str, image_path: str) -> Optional[str]:
        """
        Upload profile image to Supabase Storage.
        Returns the public URL of the uploaded image, or None if failed.
        """
        if not self.client:
            return None
            
        # DEBUG: Check session
        try:
            session = self.client.auth.get_session()
            print(f"DEBUG: Uploading for user_id: {user_id}")
            print(f"DEBUG: Session present: {session is not None}")
            if session:
                print(f"DEBUG: User in session: {session.user.id if session.user else 'No user in session'}")
                print(f"DEBUG: Token starts with: {session.access_token[:10]}...")
        except Exception as debug_err:
            print(f"DEBUG ERROR: {debug_err}")
        
        try:
            # Extract file extension
            _, ext = os.path.splitext(image_path)
            if not ext:
                ext = '.jpg'
            
            # Create file path in storage: user_id/avatar{ext}
            storage_path = f"{user_id}/avatar{ext}"
            print(f"DEBUG: Storage path: {storage_path}")
            
            # Read the file
            with open(image_path, 'rb') as f:
                file_data = f.read()
            
            # Upload to storage (will overwrite if exists)
            response = self.client.storage.from_(self.bucket_name).upload(
                storage_path,
                file_data,
                file_options={"content-type": f"image/{ext[1:]}", "upsert": "true"}
            )
            
            # Get public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(storage_path)
            
            # Update profile table with avatar URL
            self.client.table('profiles').update({'avatar_url': public_url}).eq('id', user_id).execute()
            
            return public_url
        except Exception as e:
            print(f"Error uploading profile image: {e}")
            return None

    def get_profile_image_url(self, user_id: str) -> Optional[str]:
        """
        Get the public URL for the user's profile image.
        Returns URL or None if not found.
        """
        profile = self.get_user_profile(user_id)
        if profile and 'avatar_url' in profile:
            return profile['avatar_url']
        return None

    def ensure_profile_exists(self, user_id: str, email: str, metadata: Dict = None) -> Dict[str, Any]:
        """
        Ensure a profile exists for the user. If not, create one.
        Also updates profile with any metadata from auth (like Google sign-in data).
        Returns the profile data.
        """
        profile = self.get_user_profile(user_id)
        
        if not profile:
            # Create profile from metadata if available
            first_name = ""
            last_name = ""
            
            if metadata:
                first_name = metadata.get('given_name', metadata.get('first_name', ''))
                last_name = metadata.get('family_name', metadata.get('last_name', ''))
                
                # Handle full_name if individual names not available
                if not first_name and 'full_name' in metadata:
                    parts = metadata['full_name'].split(' ', 1)
                    first_name = parts[0]
                    if len(parts) > 1:
                        last_name = parts[1]
            
            self.create_user_profile(user_id, email, first_name, last_name)
            profile = self.get_user_profile(user_id)
        
        return profile or {}
