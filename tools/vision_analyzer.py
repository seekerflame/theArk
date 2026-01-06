#!/usr/bin/env python3
"""
ARK VISION ANALYZER - Multimodal Intelligence
Uses LLaVA to analyze images and generate insights.
Can analyze: hardware builds, sensor outputs, kiosk deployments, team photos
"""
import requests
import base64
import json
import sys
from pathlib import Path
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llava:7b"

def encode_image(image_path):
    """Encode image to base64 for Ollama"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def analyze_image(image_path, prompt=None):
    """Send image to LLaVA for analysis"""
    if not Path(image_path).exists():
        return {"error": f"Image not found: {image_path}"}
    
    default_prompt = """Analyze this image for the Abundance Token / OSE Civilization OS project.
Describe what you see and provide insights on:
1. What is depicted
2. How it relates to building sovereign infrastructure
3. Any actionable observations
4. A one-line caption for documentation

Be concise but thorough. Speak as a mission-aligned AI collaborator."""

    prompt = prompt or default_prompt
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "images": [encode_image(image_path)],
                "stream": False
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "status": "success",
                "analysis": result.get("response", ""),
                "model": MODEL,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"error": f"Ollama error: {response.status_code}"}
            
    except Exception as e:
        return {"error": str(e)}

def analyze_hardware(image_path):
    """Specialized analysis for hardware/builds"""
    prompt = """You are analyzing a photo of hardware, machinery, or a build for an Open Source Ecology project.

Identify:
1. What hardware/equipment is shown
2. Estimated completion/quality level (0-100%)
3. Potential improvements or safety concerns
4. Materials visible
5. Suggested next build steps

Speak as a technical collaborator. Be specific and actionable."""
    
    return analyze_image(image_path, prompt)

def analyze_kiosk(image_path):
    """Analyze kiosk deployment photos"""
    prompt = """You are analyzing a photo of a Civilization OS kiosk deployment (The Mirror).

Assess:
1. Location suitability (foot traffic, visibility)
2. Hardware setup (screen, accessibility)
3. Brand presence (is it inviting? sovereign?)
4. Suggested improvements
5. Estimated daily user potential

Speak as a deployment strategist."""
    
    return analyze_image(image_path, prompt)

def generate_quest_from_image(image_path):
    """Generate a quest based on what's in an image"""
    prompt = """You are looking at a photo of a location or task that needs to be done.

Generate an Abundance Token quest based on what you see:
{
  "title": "...",
  "description": "...",
  "estimated_hours": X,
  "suggested_at_reward": X,
  "category": "labor|social|knowledge|hardware",
  "verification_method": "..."
}

Return ONLY the JSON. Make it realistic and actionable."""
    
    result = analyze_image(image_path, prompt)
    
    if result.get("status") == "success":
        # Try to parse JSON from response
        try:
            analysis = result["analysis"]
            # Find JSON in response
            start = analysis.find("{")
            end = analysis.rfind("}") + 1
            if start != -1 and end > start:
                quest_json = json.loads(analysis[start:end])
                result["quest"] = quest_json
        except:
            pass
    
    return result

def main():
    """CLI interface for vision analysis"""
    import argparse
    parser = argparse.ArgumentParser(description='Ark Vision Analyzer')
    parser.add_argument('image', help='Path to image file')
    parser.add_argument('--mode', choices=['general', 'hardware', 'kiosk', 'quest'], 
                       default='general', help='Analysis mode')
    parser.add_argument('--prompt', type=str, help='Custom prompt')
    args = parser.parse_args()
    
    print(f"🔍 Analyzing: {args.image}")
    print(f"📋 Mode: {args.mode}")
    print("-" * 50)
    
    if args.mode == 'hardware':
        result = analyze_hardware(args.image)
    elif args.mode == 'kiosk':
        result = analyze_kiosk(args.image)
    elif args.mode == 'quest':
        result = generate_quest_from_image(args.image)
    else:
        result = analyze_image(args.image, args.prompt)
    
    if result.get("status") == "success":
        print("✅ ANALYSIS:")
        print(result.get("analysis", ""))
        if "quest" in result:
            print("\n📋 GENERATED QUEST:")
            print(json.dumps(result["quest"], indent=2))
    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == '__main__':
    main()
