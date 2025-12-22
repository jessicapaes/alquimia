"""
Pinterest Integration Module for Realize Vision Board
Handles OAuth authentication, board/pin fetching, and image downloading
"""

import requests
import json
import os
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs, quote
import streamlit as st
from PIL import Image
import io


class PinterestAPI:
    """Pinterest API client for fetching boards and pins"""
    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.base_url = "https://api.pinterest.com/v5"
        self.headers = {
            "Authorization": f"Bearer {access_token}" if access_token else None
        }
    
    def get_user_boards(self, limit: int = 50) -> List[Dict]:
        """Fetch user's Pinterest boards"""
        if not self.access_token:
            return []
        
        try:
            response = requests.get(
                f"{self.base_url}/boards",
                headers=self.headers,
                params={"page_size": min(limit, 250)}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except Exception as e:
            st.error(f"Error fetching boards: {e}")
            return []
    
    def get_board_pins(self, board_id: str, limit: int = 50) -> List[Dict]:
        """Fetch pins from a specific board"""
        if not self.access_token:
            return []
        
        try:
            response = requests.get(
                f"{self.base_url}/boards/{board_id}/pins",
                headers=self.headers,
                params={"page_size": min(limit, 250)}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except Exception as e:
            st.error(f"Error fetching pins: {e}")
            return []
    
    def get_pin_details(self, pin_id: str) -> Optional[Dict]:
        """Get detailed information about a specific pin"""
        if not self.access_token:
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/pins/{pin_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error fetching pin details: {e}")
            return None


def extract_pinterest_url_info(url: str) -> Dict[str, Optional[str]]:
    """
    Extract board or pin information from a Pinterest URL
    Supports various Pinterest URL formats
    """
    try:
        parsed = urlparse(url)
        
        # Handle different Pinterest URL formats
        path_parts = parsed.path.strip('/').split('/')
        
        result = {
            "url": url,
            "type": None,
            "board_id": None,
            "pin_id": None,
            "username": None
        }
        
        if 'pinterest.com' in parsed.netloc or 'pinterest.' in parsed.netloc:
            # Format: /username/board-name/
            # Format: /pin/pin-id/
            # Format: /username/board-name/pin-title-pin-id/
            
            if len(path_parts) >= 2:
                result["username"] = path_parts[0]
                
                if path_parts[1] == 'pin':
                    result["type"] = "pin"
                    if len(path_parts) >= 3:
                        # Extract pin ID (usually at the end after dashes)
                        pin_part = path_parts[2]
                        result["pin_id"] = pin_part.split('-')[-1] if '-' in pin_part else pin_part
                else:
                    result["type"] = "board"
                    result["board_name"] = '/'.join(path_parts[1:])
                    
                    # Check if it's a pin URL with board context
                    if len(path_parts) >= 3:
                        pin_part = path_parts[-1]
                        if pin_part:
                            result["pin_id"] = pin_part.split('-')[-1] if '-' in pin_part else pin_part
        
        return result
    except Exception as e:
        st.error(f"Error parsing Pinterest URL: {e}")
        return {"url": url, "type": None, "board_id": None, "pin_id": None, "username": None}


def download_image_from_url(image_url: str) -> Optional[Image.Image]:
    """Download an image from a URL and return as PIL Image"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        img = Image.open(io.BytesIO(response.content))
        return img
    except Exception as e:
        st.warning(f"Could not download image from {image_url}: {e}")
        return None


def fetch_pinterest_board_images(url: str, max_images: int = 20) -> List[Image.Image]:
    """
    Fetch images from a Pinterest board URL
    This is a simplified version that works with public boards via web scraping
    For private boards, OAuth authentication is required
    """
    images = []
    
    try:
        # For public boards, we can try to scrape
        # Note: Pinterest has rate limiting and may block requests
        # For production, use official Pinterest API with OAuth
        
        parsed_info = extract_pinterest_url_info(url)
        
        if parsed_info["type"] == "pin":
            # Single pin - try to get the image
            pin_id = parsed_info.get("pin_id")
            if pin_id:
                # Try to construct image URL (this is a workaround)
                # In production, use Pinterest API
                st.info("💡 For best results, use Pinterest API authentication to fetch pin images.")
                st.info("💡 Alternatively, you can manually upload images or use Pinterest's embed features.")
        
        elif parsed_info["type"] == "board":
            st.info("💡 To fetch images from Pinterest boards, you need to:")
            st.info("1. Set up Pinterest API credentials (App ID and Secret)")
            st.info("2. Authenticate via OAuth to get an access token")
            st.info("3. Use the Pinterest API to fetch board pins")
            st.info("")
            st.info("For now, you can manually upload images or paste individual pin image URLs.")
        
    except Exception as e:
        st.error(f"Error fetching Pinterest images: {e}")
    
    return images


def get_pinterest_oauth_url(app_id: str, redirect_uri: str, scopes: List[str] = None) -> str:
    """Generate Pinterest OAuth authorization URL"""
    if scopes is None:
        scopes = ["boards:read", "pins:read"]
    
    scope_string = ",".join(scopes)
    
    oauth_url = (
        f"https://www.pinterest.com/oauth/?"
        f"client_id={app_id}&"
        f"redirect_uri={quote(redirect_uri)}&"
        f"response_type=code&"
        f"scope={scope_string}"
    )
    
    return oauth_url


def exchange_code_for_token(
    app_id: str, 
    app_secret: str, 
    code: str, 
    redirect_uri: str
) -> Optional[str]:
    """Exchange OAuth authorization code for access token"""
    try:
        response = requests.post(
            "https://api.pinterest.com/v5/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": app_id,
                "client_secret": app_secret,
                "code": code,
                "redirect_uri": redirect_uri
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("access_token")
    except Exception as e:
        st.error(f"Error exchanging code for token: {e}")
        return None


def map_pins_to_vision_areas(
    pins: List[Dict], 
    vision_areas: Dict[str, Dict],
    smart_goals: List[Dict]
) -> Dict[str, List[Dict]]:
    """
    Intelligently map Pinterest pins to vision board areas
    based on pin title, description, and user's goals
    """
    mapping = {area: [] for area in vision_areas.keys()}
    
    # Extract keywords from vision areas
    area_keywords = {}
    for area, details in vision_areas.items():
        keywords = details.get("keywords", [])
        # Also extract keywords from goals related to this area
        area_emoji = area.split()[0] if area.split() else ""
        area_keywords[area] = [kw.lower() for kw in keywords]
    
    # Map pins to areas based on keywords
    for pin in pins:
        pin_text = ""
        if "title" in pin:
            pin_text += pin["title"].lower() + " "
        if "description" in pin:
            pin_text += pin["description"].lower() + " "
        if "note" in pin:
            pin_text += pin["note"].lower() + " "
        
        best_match = None
        best_score = 0
        
        for area, keywords in area_keywords.items():
            score = sum(1 for keyword in keywords if keyword in pin_text)
            if score > best_score:
                best_score = score
                best_match = area
        
        if best_match and best_score > 0:
            mapping[best_match].append(pin)
        else:
            # If no match, add to first area (user can manually reassign)
            first_area = list(vision_areas.keys())[0]
            mapping[first_area].append(pin)
    
    return mapping

