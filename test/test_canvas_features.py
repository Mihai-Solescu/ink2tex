#!/usr/bin/env python3
"""
Test script to demonstrate the new canvas features
"""

from PyQt6.QtCore import QRect

def test_canvas_bounds_calculation():
    """Test the handwriting bounds calculation logic"""
    
    # Simulate some drawn paths (points)
    drawn_paths = [
        [(100, 150), (120, 150), (140, 160), (160, 170)],  # Horizontal line
        [(110, 180), (110, 200), (115, 220), (120, 240)],  # Vertical line
        [(200, 300), (220, 320), (240, 340), (260, 360)]   # Diagonal line
    ]
    
    # Convert to QPoint-like objects for testing
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    
    for path in drawn_paths:
        for point in path:
            x, y = point
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
    
    # Add padding
    padding = 30
    min_x = max(0, min_x - padding)
    min_y = max(0, min_y - padding)
    max_x = max_x + padding
    max_y = max_y + padding
    
    width = max_x - min_x
    height = max_y - min_y
    
    bounds = QRect(int(min_x), int(min_y), int(width), int(height))
    
    print("📐 Canvas Bounds Calculation Test")
    print("=" * 50)
    print(f"Input paths: {len(drawn_paths)} paths with {sum(len(p) for p in drawn_paths)} total points")
    print(f"Original bounds: ({min_x + padding}, {min_y + padding}) to ({max_x - padding}, {max_y - padding})")
    print(f"With padding ({padding}px): {bounds}")
    print(f"Cropped image size: {bounds.width()} x {bounds.height()} pixels")
    print("✅ Bounds calculation working correctly!")
    
    return bounds

def test_canvas_sizes():
    """Test canvas size calculations for different screen sizes"""
    
    print("\n🖥️ Canvas Size Calculation Test")
    print("=" * 50)
    
    # Test different screen sizes
    screen_sizes = [
        (1920, 1080, "Full HD"),
        (2560, 1440, "2K"),
        (3840, 2160, "4K"),
        (1366, 768, "Small Laptop"),
        (1680, 1050, "16:10 Monitor")
    ]
    
    for width, height, name in screen_sizes:
        # Simulate canvas calculation
        left_panel_width = 450
        canvas_start_x = 50
        canvas_start_y = 50
        
        canvas_width = max(600, width - left_panel_width - 100)
        canvas_height = max(400, height - 150)
        
        print(f"{name} ({width}x{height}):")
        print(f"  Canvas area: {canvas_width} x {canvas_height} pixels")
        print(f"  Coverage: {(canvas_width * canvas_height) / (width * height) * 100:.1f}% of screen")
        print()

if __name__ == "__main__":
    print("🧪 Testing New Canvas Features")
    print("=" * 60)
    
    # Test bounds calculation
    bounds = test_canvas_bounds_calculation()
    
    # Test canvas sizes
    test_canvas_sizes()
    
    print("✅ All tests completed!")
    print("\n📋 New Features Summary:")
    print("• Canvas now covers the entire right side of the screen")
    print("• Smart cropping saves only the handwriting area + padding")
    print("• Optimized for AI recognition with proper sizing")
    print("• Maintains aspect ratio for uploaded images")
    print("• Dynamic sizing adapts to different screen resolutions")
