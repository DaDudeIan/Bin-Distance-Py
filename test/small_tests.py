import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import entities
from world.world import World
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

def visualize_paths(world):
    """Visualize the paths from doors to bins on the original image"""
    if world.img is None:
        return
    
    # Create a copy of the original image for visualization
    vis_img = world.img.copy()
    
    # Define colors for different paths (BGR format for OpenCV)
    colors = [
        (0, 255, 0),    # Green
        (255, 0, 0),    # Blue  
        (0, 0, 255),    # Red
        (255, 255, 0),  # Cyan
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Yellow
    ]
    
    # Draw paths for each door, colored by destination bin
    for door in world.doors:
        if door.path_to_bin is not None and door.assigned_bin is not None:
            # Use bin number to determine color (bin numbers start from 1)
            color = colors[(door.assigned_bin - 1) % len(colors)]
            
            # Draw the path
            for j, (y, x) in enumerate(door.path_to_bin):
                # Draw path points
                cv2.circle(vis_img, (x, y), 1, color, -1)
                
                # Draw lines between consecutive path points
                if j > 0:
                    prev_y, prev_x = door.path_to_bin[j-1]
                    cv2.line(vis_img, (prev_x, prev_y), (x, y), color, 1)
    
    # Draw doors and bins with labels
    # for door in world.doors:
    #     # Draw door circle
    #     cv2.circle(vis_img, (door.x, door.y), 5, (255, 255, 255), 2)  # White circle
    #     cv2.putText(vis_img, f'D{door.number}', (door.x + 7, door.y - 7), 
    #                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    for bin_entity in world.bins:
        # Draw bin circle
        cv2.circle(vis_img, (bin_entity.x, bin_entity.y), 5, (0, 0, 0), 2)  # Black circle
        # cv2.putText(vis_img, f'B{bin_entity.number}', (bin_entity.x + 7, bin_entity.y - 7), 
        #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    # Display the image using matplotlib
    # Convert from BGR to RGB for matplotlib
    vis_img_rgb = cv2.cvtColor(vis_img, cv2.COLOR_BGR2RGB)
    
    plt.figure(figsize=(12, 8))
    plt.imshow(vis_img_rgb)
    plt.title(f'Door-to-Bin Path Assignments: {world.name}')
    plt.axis('off')
    
    # Add legend - group by bin
    legend_elements = []
    bins_with_doors = set()
    
    # Collect which bins have doors assigned to them
    for door in world.doors:
        if door.assigned_bin is not None:
            bins_with_doors.add(door.assigned_bin)
    
    # Calculate total doors with assignments for percentage calculation
    total_assigned_doors = len([door for door in world.doors if door.assigned_bin is not None])
    
    # Create legend entries for each bin that has doors
    for bin_num in sorted(bins_with_doors):
        bgr_color = colors[(bin_num - 1) % len(colors)]
        # Convert BGR to RGB and normalize to 0-1 range
        rgb_color = (bgr_color[2]/255.0, bgr_color[1]/255.0, bgr_color[0]/255.0)
        
        # Count doors going to this bin
        door_count = len([door for door in world.doors if door.assigned_bin == bin_num])
        
        # Calculate percentage
        percentage = (door_count / total_assigned_doors * 100) if total_assigned_doors > 0 else 0
        
        legend_elements.append(Line2D([0], [0], color=rgb_color, lw=2, 
                                    label=f'B{bin_num}: {door_count} doors ({percentage:.1f}%)'))
    
    if legend_elements:
        plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
    
    plt.tight_layout()
    
    # Save the matplotlib version
    output_path_plt = "./test/path_visualization_matplotlib.png"
    plt.savefig(output_path_plt, dpi=150, bbox_inches='tight')
    
    # # Only show if in interactive environment
    # try:
    #     plt.show()
    # except:
    #     pass  # Non-interactive environment
    
    # Save the OpenCV version  
    output_path = "./test/path_visualization.jpg"
    #cv2.imwrite(output_path, vis_img)

def create_simple_visualization(world):
    """Create a simple, clear visualization with thicker lines and better labels"""
    if world.img is None:
        return
    
    # Create a copy of the original image for visualization
    vis_img = world.img.copy()
    
    # Define distinct colors for different paths (BGR format for OpenCV)
    colors = [
        (0, 255, 0),    # Bright Green
        (255, 0, 0),    # Bright Blue  
        (0, 0, 255),    # Bright Red
        (255, 255, 0),  # Bright Cyan
        (255, 0, 255),  # Bright Magenta
        (0, 255, 255),  # Bright Yellow
    ]
    
    # Group doors by their assigned bins for clearer output
    bins_with_doors = {}
    for door in world.doors:
        if door.assigned_bin is not None:
            if door.assigned_bin not in bins_with_doors:
                bins_with_doors[door.assigned_bin] = []
            bins_with_doors[door.assigned_bin].append(door)
    
    # Draw paths for each door, colored by destination bin
    for bin_num, doors_list in sorted(bins_with_doors.items()):
        color = colors[(bin_num - 1) % len(colors)]
        
        for door in doors_list:
            if door.path_to_bin is not None:
                # Draw the path with thicker lines
                path_points = [(x, y) for y, x in door.path_to_bin]  # Convert (y,x) to (x,y)
                
                if len(path_points) > 1:
                    # Draw path as connected lines
                    for j in range(len(path_points) - 1):
                        cv2.line(vis_img, path_points[j], path_points[j + 1], color, 2)
                
                # Draw small circles along the path for clarity
                for x, y in path_points[::5]:  # Every 5th point to avoid clutter
                    cv2.circle(vis_img, (x, y), 1, color, -1)
    
    # Draw doors with distinct markers
    for door in world.doors:
        # Draw door with a larger white circle and black border
        cv2.circle(vis_img, (door.x, door.y), 8, (255, 255, 255), -1)  # White filled circle
        cv2.circle(vis_img, (door.x, door.y), 8, (0, 0, 0), 2)         # Black border
        cv2.putText(vis_img, f'D{door.number}', (door.x - 8, door.y - 12), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    # Draw bins with distinct markers
    for bin_entity in world.bins:
        # Draw bin with a larger black circle and white border
        cv2.circle(vis_img, (bin_entity.x, bin_entity.y), 8, (0, 0, 0), -1)    # Black filled circle
        cv2.circle(vis_img, (bin_entity.x, bin_entity.y), 8, (255, 255, 255), 2) # White border
        cv2.putText(vis_img, f'B{bin_entity.number}', (bin_entity.x - 8, bin_entity.y - 12), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Add text overlay with distribution percentages
    total_assigned_doors = len([door for door in world.doors if door.assigned_bin is not None])
    
    if total_assigned_doors > 0:
        y_offset = 30
        cv2.putText(vis_img, "Distribution:", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        for bin_num in sorted(bins_with_doors.keys()):
            door_count = len(bins_with_doors[bin_num])
            percentage = (door_count / total_assigned_doors * 100)
            y_offset += 25
            
            # Use the same color as the paths
            bgr_color = colors[(bin_num - 1) % len(colors)]
            
            text = f"B{bin_num}: {door_count} doors ({percentage:.1f}%)"
            cv2.putText(vis_img, text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, bgr_color, 2)
    
    # Save the simple visualization
    output_path = "./test/simple_path_visualization.jpg"
    cv2.imwrite(output_path, vis_img)
    
    return vis_img

def main():
    w = World("Ulige numre", "./test/rs_ulige.jpg")
    w.find_paths()
    
    # Create visualizations
    visualize_paths(w)
    #create_simple_visualization(w)

if __name__ == "__main__":
    main()