import bpy
import numpy as np
import random
import math
import os
import time
import urllib.request
from mathutils import Vector, Euler, Matrix, Quaternion


# Set absolute path for output
#OUTPUT_DIR = "D:/WPI_Assignments/Computer_Vision_CS549/YourDirectoryID_p4/YourDirectoryID_p4/Phase2_Data"
#TEXTURES_PATH = "D:/WPI_Assignments/Computer_Vision_CS549/YourDirectoryID_p4/YourDirectoryID_p4/data/textures"
BLEND_FILE_DIR = os.path.dirname(bpy.data.filepath)
OUTPUT_DIR = os.path.join(BLEND_FILE_DIR, "Phase2_Data")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define training and testing splits
TRAIN_TRAJECTORIES = ["oval", "figure8", "clover", "wavy_circle", "line", "star"]
TEST_TRAJECTORIES = ["spiral", "infinity", "random"]

def print_log(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

def setup_scene():
    print_log("Setting up scene")
    
    # Clear everything first
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create large plane (75x75 meters)
    bpy.ops.mesh.primitive_plane_add(size=75, location=(0, 0, 0))
    plane = bpy.context.active_object
    plane.name = "Floor"
    
    # Create light
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    light = bpy.context.active_object
    light.data.energy = 5.0
    
    # Create downward-facing camera
    bpy.ops.object.camera_add(location=(0, 0, 10), rotation=(math.radians(90), 0, 0))
    camera = bpy.context.active_object
    camera.name = "Camera"
    bpy.context.scene.camera = camera
    
    # Set render settings - use EEVEE for fast rendering
    try:
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        try:
            bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
        except TypeError:
            bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.cycles.samples = 32
    
    # Set material preview mode for fast rendering
    bpy.context.scene.render.resolution_x = 640
    bpy.context.scene.render.resolution_y = 480
    
    # Fix camera intrinsics (K matrix)
    camera.data.lens = 35.0  # fixed focal length
    camera.data.sensor_width = 36.0
    
    print_log("Scene setup complete")
    return plane, camera

def download_random_texture():
    """Download a random texture from a collection of URLs"""
    texture_urls = [
        "https://images.pexels.com/photos/1939485/pexels-photo-1939485.jpeg",
        "https://images.pexels.com/photos/3951516/pexels-photo-3951516.jpeg",
        "https://images.pexels.com/photos/247431/pexels-photo-247431.jpeg",
        "https://images.pexels.com/photos/326333/pexels-photo-326333.jpeg"
    ]
    
    temp_file = os.path.join(OUTPUT_DIR, "temp_texture.jpg")
    url = random.choice(texture_urls)
    
    try:
        urllib.request.urlretrieve(url, temp_file)
        return temp_file
    except:
        print_log(f"Failed to download texture from {url}")
        return None

def apply_floor_texture(plane):
    print_log("Applying texture to floor plane")
    
    # Create material
    material = bpy.data.materials.new(name="FloorMaterial")
    plane.data.materials.append(material)
    material.use_nodes = True
    
    # Access nodes
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    # Clear default nodes
    for node in nodes:
        nodes.remove(node)
    
    # Create nodes
    output_node = nodes.new('ShaderNodeOutputMaterial')
    principled_node = nodes.new('ShaderNodeBsdfPrincipled')
    texture_node = nodes.new('ShaderNodeTexImage')
    mapping_node = nodes.new('ShaderNodeMapping')
    tex_coord_node = nodes.new('ShaderNodeTexCoord')
    
    # List your texture paths
    texture_paths = [
#        os.path.join(BLEND_FILE_DIR, "elephant_forest.jpg"),
#        os.path.join(BLEND_FILE_DIR, "skyline.jpg"),
        os.path.join(BLEND_FILE_DIR, "city.jpg")
#        os.path.join(BLEND_FILE_DIR, "wood_texture.jpg")
        # Add more paths as needed
    ]
    
    # Choose a random texture
    texture_path = random.choice(texture_paths)
    
    try:
        # Load the texture
        texture_node.image = bpy.data.images.load(texture_path)
        print_log(f"Using texture: {texture_path}")
    except Exception as e:
        print_log(f"Failed to load texture: {e}, using procedural texture")
        
        # Create a noise texture with better features for tracking
        noise_node = nodes.new('ShaderNodeTexNoise')
        noise_node.inputs['Scale'].default_value = 25.0
        noise_node.inputs['Detail'].default_value = 10.0
        noise_node.inputs['Roughness'].default_value = 0.7
        
        # Connect noise nodes
        links.new(tex_coord_node.outputs['UV'], mapping_node.inputs['Vector'])
        links.new(mapping_node.outputs['Vector'], noise_node.inputs['Vector'])
        links.new(noise_node.outputs['Color'], principled_node.inputs['Base Color'])
    else:
        # Connect texture nodes
        links.new(tex_coord_node.outputs['UV'], mapping_node.inputs['Vector'])
        links.new(mapping_node.outputs['Vector'], texture_node.inputs['Vector'])
        links.new(texture_node.outputs['Color'], principled_node.inputs['Base Color'])
    
    # Connect output
    links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    
    # Apply appropriate scaling to texture (small values = large texture)
    scale_factor = random.uniform(0.2, 0.5)
    
    # Apply random offset to avoid centered textures
    x_offset = random.uniform(0, 0.5)
    y_offset = random.uniform(0, 0.5)
    
    # Set mapping node parameters
    if hasattr(mapping_node.inputs[3], 'default_value'):
        # Older Blender versions
        mapping_node.inputs[1].default_value = (x_offset, y_offset, 0)  # Location
        mapping_node.inputs[3].default_value = (scale_factor, scale_factor, scale_factor)  # Scale
    else:
        # Newer Blender versions
        mapping_node.inputs['Location'].default_value = (x_offset, y_offset, 0)
        mapping_node.inputs['Scale'].default_value = (scale_factor, scale_factor, scale_factor)
    
    return material.name

def create_procedural_texture():
    """Create a procedural texture with good features for tracking"""
    size = 2048
    image = bpy.data.images.new("FloorTexture", width=size, height=size)
    
    # Fill with random pattern that has good features for tracking
    pixels = [None] * size * size * 4
    for y in range(size):
        for x in range(size):
            # Create a pattern with varied frequencies
            r = 0.5 + 0.5 * math.sin(x/50) * math.cos(y/70)
            g = 0.5 + 0.5 * math.sin(x/80) * math.cos(y/60)
            b = 0.5 + 0.5 * math.sin(x/100) * math.cos(y/90)
            
            idx = (y * size + x) * 4
            pixels[idx] = r
            pixels[idx+1] = g
            pixels[idx+2] = b
            pixels[idx+3] = 1.0
    
    image.pixels = pixels
    return image

def generate_trajectory(trajectory_type, num_points=5000, z_height=5.0):
    print_log(f"Generating {trajectory_type} trajectory")
    
    points = []
    orientations = []
    t_values = np.linspace(0, 2*np.pi, num_points)
    
    # Maximum angle for roll and pitch (45 degrees max)
    max_roll_pitch = math.radians(45)
    
    if trajectory_type == "oval":
        for t in t_values:
            x = 10 * np.cos(t)
            y = 15 * np.sin(t)
            z = z_height + 0.5 * np.sin(3*t)
            
            # Calculate orientation - looking in direction of movement
            dx = -10 * np.sin(t)
            dy = 15 * np.cos(t)
            yaw = math.atan2(dy, dx)
            
            # Add controlled roll/pitch variations (within 45 degrees)
            pitch = 0.5 * max_roll_pitch * np.sin(3*t)
            roll = 0.5 * max_roll_pitch * np.cos(2*t)
            
            points.append((x, y, z))
            orientations.append((roll, pitch, yaw))
    
    elif trajectory_type == "figure8":
        for t in t_values:
            x = 15 * np.sin(t)
            y = 15 * np.sin(t) * np.cos(t)
            z = z_height + 2 * np.sin(2*t)
            
            dx = 15 * np.cos(t)
            dy = 15 * (np.cos(t) * np.cos(t) - np.sin(t) * np.sin(t))
            yaw = math.atan2(dy, dx)
            
            pitch = 0.7 * max_roll_pitch * np.sin(2*t)
            roll = 0.7 * max_roll_pitch * np.sin(3*t)
            
            points.append((x, y, z))
            orientations.append((roll, pitch, yaw))
    
    elif trajectory_type == "clover":
        for t in t_values:
            r = 15 * np.cos(2*t)
            x = r * np.cos(t)
            y = r * np.sin(t)
            z = z_height + 1.5 * np.sin(4*t)
            
            dx = -r * np.sin(t) - 30 * np.sin(2*t) * np.cos(t)
            dy = r * np.cos(t) - 30 * np.sin(2*t) * np.sin(t)
            yaw = math.atan2(dy, dx)
            
            pitch = 0.6 * max_roll_pitch * np.sin(3*t)
            roll = 0.6 * max_roll_pitch * np.cos(3*t)
            
            points.append((x, y, z))
            orientations.append((roll, pitch, yaw))
    
    elif trajectory_type == "spiral":
        for t in t_values:
            radius = 5 + 10 * t / (2*np.pi)
            x = radius * np.cos(t)
            y = radius * np.sin(t)
            z = z_height + 3 * np.sin(3*t)
            
            dx = np.cos(t) - radius * np.sin(t)
            dy = np.sin(t) + radius * np.cos(t)
            yaw = math.atan2(dy, dx)
            
            pitch = 0.5 * max_roll_pitch * np.sin(3*t)
            roll = 0.5 * max_roll_pitch * np.cos(4*t)
            
            points.append((x, y, z))
            orientations.append((roll, pitch, yaw))
    
    elif trajectory_type == "infinity":
        for t in t_values:
            x = 15 * np.sin(t)
            y = 15 * np.sin(2*t) / 2
            z = z_height + np.sin(3*t)
            
            dx = 15 * np.cos(t)
            dy = 15 * np.cos(2*t)
            yaw = math.atan2(dy, dx)
            
            pitch = 0.5 * max_roll_pitch * np.sin(2*t)
            roll = 0.3 * max_roll_pitch * np.cos(3*t)
            
            points.append((x, y, z))
            orientations.append((roll, pitch, yaw))
    
    elif trajectory_type == "wavy_circle":
        for t in t_values:
            x = 12 * np.cos(t) + 3 * np.cos(5*t)
            y = 12 * np.sin(t) + 3 * np.sin(5*t)
            z = z_height + np.sin(4*t)
            
            dx = -12 * np.sin(t) - 15 * np.sin(5*t)
            dy = 12 * np.cos(t) + 15 * np.cos(5*t)
            yaw = math.atan2(dy, dx)
            
            pitch = 0.4 * max_roll_pitch * np.sin(3*t)
            roll = 0.4 * max_roll_pitch * np.cos(2*t)
            
            points.append((x, y, z))
            orientations.append((roll, pitch, yaw))
    
    elif trajectory_type == "line":
        for t in t_values:
            # Line with sinusoidal height and slight sideways motion
            x = 20 * t / (2*np.pi) - 10
            y = 3 * np.sin(2*t)
            z = z_height + 2 * np.sin(4*t)
            
            dx = 20 / (2*np.pi)
            dy = 6 * np.cos(2*t)
            yaw = math.atan2(dy, dx)
            
            pitch = 0.4 * max_roll_pitch * np.sin(3*t)
            roll = 0.4 * max_roll_pitch * np.cos(2*t)
            
            points.append((x, y, z))
            orientations.append((roll, pitch, yaw))
    
    elif trajectory_type == "star":
        for t in t_values:
            r = 10 + 5 * np.sin(5*t)
            x = r * np.cos(t)
            y = r * np.sin(t)
            z = z_height + np.sin(3*t)
            
            dr = 25 * np.cos(5*t)
            dx = np.cos(t)*dr - r*np.sin(t)
            dy = np.sin(t)*dr + r*np.cos(t)
            yaw = math.atan2(dy, dx)
            
            pitch = 0.3 * max_roll_pitch * np.sin(2*t)
            roll = 0.3 * max_roll_pitch * np.cos(3*t)
            
            points.append((x, y, z))
            orientations.append((roll, pitch, yaw))
    
    elif trajectory_type == "random":
        # Create a random but smooth trajectory
        x_points = np.zeros(num_points)
        y_points = np.zeros(num_points)
        z_points = np.zeros(num_points) + z_height
        
        # Generate random control points and interpolate
        num_control = 8
        x_control = np.random.uniform(-15, 15, num_control)
        y_control = np.random.uniform(-15, 15, num_control)
        z_control = np.random.uniform(z_height-2, z_height+2, num_control)
        
        # Simple linear interpolation for smoothness
        for i in range(num_points):
            t_normalized = i / (num_points - 1)
            idx = int(t_normalized * (num_control - 1))
            alpha = (t_normalized * (num_control - 1)) - idx
            
            if idx < num_control - 1:
                x_points[i] = x_control[idx] * (1 - alpha) + x_control[idx + 1] * alpha
                y_points[i] = y_control[idx] * (1 - alpha) + y_control[idx + 1] * alpha
                z_points[i] = z_control[idx] * (1 - alpha) + z_control[idx + 1] * alpha
            else:
                x_points[i] = x_control[-1]
                y_points[i] = y_control[-1]
                z_points[i] = z_control[-1]
        
        # Calculate orientations based on movement direction
        for i in range(num_points):
            if i == 0:
                dx = x_points[1] - x_points[0]
                dy = y_points[1] - y_points[0]
            elif i == num_points - 1:
                dx = x_points[-1] - x_points[-2]
                dy = y_points[-1] - y_points[-2]
            else:
                dx = x_points[i+1] - x_points[i-1]
                dy = y_points[i+1] - y_points[i-1]
            
            yaw = math.atan2(dy, dx)
            pitch = 0.4 * max_roll_pitch * np.sin(i * 0.1)
            roll = 0.4 * max_roll_pitch * np.cos(i * 0.15)
            
            points.append((x_points[i], y_points[i], z_points[i]))
            orientations.append((roll, pitch, yaw))
    
    else:  # Default to a sinusoidal path
        for t in t_values:
            x = 20 * t / (2*np.pi) - 10
            y = 10 * np.sin(t)
            z = z_height + 2 * np.sin(2*t)
            
            dx = 20 / (2*np.pi)
            dy = 10 * np.cos(t)
            yaw = math.atan2(dy, dx)
            
            pitch = 0.5 * max_roll_pitch * np.sin(3*t)
            roll = 0.5 * max_roll_pitch * np.cos(2*t)
            
            points.append((x, y, z))
            orientations.append((roll, pitch, yaw))
    
    print_log(f"Generated {len(points)} trajectory points")
    return points, orientations

def simulate_imu_measurements(positions, orientations, dt=0.001, noise_level=0.01):
    """Simulate IMU measurements with OysterSim-inspired noise model"""
    print_log("Simulating IMU measurements")
    
    accel_data = []
    gyro_data = []
    time_steps = []
    
    # Gravity vector in world frame
    gravity = Vector((0, 0, -9.81))
    
    # Noise parameters (inspired by OysterSim)
    accel_noise_density = 0.002  # m/s²/√Hz
    gyro_noise_density = 0.00012  # rad/s/√Hz
    
    # Scale noise by dt to account for sampling rate
    accel_noise_scale = accel_noise_density * math.sqrt(1.0/dt)
    gyro_noise_scale = gyro_noise_density * math.sqrt(1.0/dt)
    
    # Calculate velocities using central difference
    velocities = []
    for i in range(len(positions)):
        if i == 0:
            next_pos = Vector(positions[i+1])
            curr_pos = Vector(positions[i])
            velocity = (next_pos - curr_pos) / dt
        elif i == len(positions) - 1:
            curr_pos = Vector(positions[i])
            prev_pos = Vector(positions[i-1])
            velocity = (curr_pos - prev_pos) / dt
        else:
            next_pos = Vector(positions[i+1])
            prev_pos = Vector(positions[i-1])
            velocity = (next_pos - prev_pos) / (2 * dt)
        
        velocities.append(velocity)
    
    # Calculate IMU measurements
    for i in range(len(positions)):
        roll, pitch, yaw = orientations[i]
        rot_matrix = Euler((roll, pitch, yaw), 'XYZ').to_matrix()
        
        # Calculate acceleration
        if i == 0:
            curr_vel = velocities[i]
            next_vel = velocities[i+1]
            accel_world = (next_vel - curr_vel) / dt
        elif i == len(velocities) - 1:
            curr_vel = velocities[i]
            prev_vel = velocities[i-1]
            accel_world = (curr_vel - prev_vel) / dt
        else:
            next_vel = velocities[i+1]
            prev_vel = velocities[i-1]
            accel_world = (next_vel - prev_vel) / (2 * dt)
        
        # Add gravity and convert to body frame 
        accel_with_gravity = accel_world - gravity  #accel_world - gravity 
        accel_body = rot_matrix.transposed() @ accel_with_gravity
        
        # Add noise to accelerometer
        accel_noise = [random.gauss(0, accel_noise_scale) for _ in range(3)]
        accel_body_noisy = [accel_body[j] + accel_noise[j] for j in range(3)]
        
        # Calculate angular velocity
        if i == 0:
            next_roll, next_pitch, next_yaw = orientations[i+1]
            curr_roll, curr_pitch, curr_yaw = orientations[i]
            
            # Unwrap yaw for continuity
            if next_yaw - curr_yaw > math.pi:
                next_yaw -= 2 * math.pi
            elif curr_yaw - next_yaw > math.pi:
                next_yaw += 2 * math.pi
                
            d_roll = (next_roll - curr_roll) / dt
            d_pitch = (next_pitch - curr_pitch) / dt
            d_yaw = (next_yaw - curr_yaw) / dt
            
        elif i == len(orientations) - 1:
            curr_roll, curr_pitch, curr_yaw = orientations[i]
            prev_roll, prev_pitch, prev_yaw = orientations[i-1]
            
            # Unwrap yaw
            if curr_yaw - prev_yaw > math.pi:
                prev_yaw += 2 * math.pi
            elif prev_yaw - curr_yaw > math.pi:
                prev_yaw -= 2 * math.pi
                
            d_roll = (curr_roll - prev_roll) / dt
            d_pitch = (curr_pitch - prev_pitch) / dt
            d_yaw = (curr_yaw - prev_yaw) / dt
            
        else:
            next_roll, next_pitch, next_yaw = orientations[i+1]
            prev_roll, prev_pitch, prev_yaw = orientations[i-1]
            
            # Unwrap yaw
            if next_yaw - prev_yaw > math.pi:
                next_yaw -= 2 * math.pi
            elif prev_yaw - next_yaw > math.pi:
                next_yaw += 2 * math.pi
                
            d_roll = (next_roll - prev_roll) / (2 * dt)
            d_pitch = (next_pitch - prev_pitch) / (2 * dt)
            d_yaw = (next_yaw - prev_yaw) / (2 * dt)
        
        # Angular velocities in body frame
        gyro_body = [d_roll, d_pitch, d_yaw]
        
        # Add noise to gyroscope
        gyro_noise = [random.gauss(0, gyro_noise_scale) for _ in range(3)]
        gyro_body_noisy = [gyro_body[j] + gyro_noise[j] for j in range(3)]
        
        time_steps.append(i * dt)
        accel_data.append(accel_body_noisy)
        gyro_data.append(gyro_body_noisy)
    
    return time_steps, accel_data, gyro_data

def calculate_relative_poses(positions, orientations, camera_interval=1):
    print_log("Calculating relative poses")
    
    relative_poses = []
    
    # Get camera frame indices
    camera_indices = list(range(0, len(positions), camera_interval))
    
    # Calculate relative poses between consecutive camera frames
    for i in range(1, len(camera_indices)):
        prev_idx = camera_indices[i-1]
        curr_idx = camera_indices[i]
        
        prev_pos = Vector(positions[prev_idx])
        curr_pos = Vector(positions[curr_idx])
        
        prev_rot = Euler(orientations[prev_idx], 'XYZ')
        curr_rot = Euler(orientations[curr_idx], 'XYZ')
        
        # Create rotation matrices
        prev_rot_matrix = prev_rot.to_matrix()
        curr_rot_matrix = curr_rot.to_matrix()
        
        # Calculate relative rotation
        rel_rot_matrix = prev_rot_matrix.transposed() @ curr_rot_matrix
        rel_rot = rel_rot_matrix.to_euler()
        
        # Calculate relative position (in previous frame's coordinate system)
        rel_pos = prev_rot_matrix.transposed() @ (curr_pos - prev_pos)
        
        relative_poses.append({
            'prev_frame': prev_idx // camera_interval,
            'curr_frame': curr_idx // camera_interval,
            'position': rel_pos,
            'rotation': rel_rot
        })
    
    return relative_poses

def generate_dataset(trajectory_type, output_path, is_training=True):
    print_log(f"Generating dataset for {trajectory_type} ({'training' if is_training else 'testing'})")
    
    # Setup scene with downward-facing camera
    plane, camera = setup_scene()
    apply_floor_texture(plane)
    
    # Fixed parameters
    duration = 5.0  # Fixed 5-second duration
    imu_rate = 1000  # 1000Hz IMU
    camera_rate = 100  # 100Hz camera
    
    # Determine dataset type
    dataset_type = "train" if is_training else "test"
    
    # Create output directories
    base_dir = os.path.join(output_path, dataset_type, f"{trajectory_type}")
    
    # Create directories for different network types
    vis_dir = os.path.join(base_dir, "vision_only")
    imu_dir = os.path.join(base_dir, "imu_only")
    vi_dir = os.path.join(base_dir, "visual_inertial")
    
    for dir_path in [vis_dir, imu_dir, vi_dir]:
        os.makedirs(os.path.join(dir_path, "images"), exist_ok=True)
    
    # Calculate required number of points
    num_imu_points = int(duration * imu_rate)  # 5000 IMU points
    camera_interval = imu_rate // camera_rate  # Every 10th IMU reading

    
    # Generate trajectory
    positions, orientations = generate_trajectory(trajectory_type, num_points=num_imu_points)
    
    # Scale time step by speed factor
#    dt = 0.001 / speed_factor  # 1000Hz IMU base rate
    dt = 1.0 / imu_rate  # 0.001 seconds (1ms) per IMU reading

    camera_interval = 10  # Camera at 100Hz (every 10th IMU sample)
    
    # Simulate IMU data
    times, accel_data, gyro_data = simulate_imu_measurements(positions, orientations, dt)
    
    # Calculate relative poses between camera frames
    relative_poses = calculate_relative_poses(positions, orientations, camera_interval)
    
    # Save camera intrinsics
    focal_length = camera.data.lens
    sensor_width = camera.data.sensor_width
    render_width = bpy.context.scene.render.resolution_x
    render_height = bpy.context.scene.render.resolution_y
    
    # Calculate focal length in pixels
    fx = focal_length / sensor_width * render_width
    fy = fx
    
    # Principal point at center
    cx = render_width / 2
    cy = render_height / 2
    
    # Save camera intrinsics to all dataset types
    for dir_path in [vis_dir, imu_dir, vi_dir]:
        with open(os.path.join(dir_path, "camera_intrinsics.txt"), 'w') as f:
            f.write(f"fx,fy,cx,cy\n")
            f.write(f"{fx},{fy},{cx},{cy}\n")
    
    # Save absolute camera poses for all dataset types
    for dir_path in [vis_dir, imu_dir, vi_dir]:
        with open(os.path.join(dir_path, "camera_poses.txt"), 'w') as f:
            f.write("frame,timestamp,pos_x,pos_y,pos_z,rot_x,rot_y,rot_z\n")
            for i in range(0, len(positions), camera_interval):
                frame_idx = i // camera_interval
                timestamp = times[i] if i < len(times) else times[-1]
                f.write(f"{frame_idx},{timestamp},{positions[i][0]},{positions[i][1]},{positions[i][2]},")
                f.write(f"{orientations[i][0]},{orientations[i][1]},{orientations[i][2]}\n")
    
    # Save relative poses for all dataset types
    for dir_path in [vis_dir, imu_dir, vi_dir]:        
        with open(os.path.join(dir_path, "relative_poses.txt"), 'w') as f:
#           f.write("prev_frame,curr_frame,rel_pos_x,rel_pos_y,rel_pos_z,rel_rot_x,rel_rot_y,rel_rot_z\n")
            f.write("prev_frame,curr_frame,tx,ty,tz,qw,qx,qy,qz\n")
            for rel_pose in relative_poses:
                # current code already has rel_pose['rotation'] as a mathutils.Matrix or Euler.
                # Convert it once here:
                rel_q = rel_pose['rotation'].to_quaternion()

                f.write(f"{rel_pose['prev_frame']},{rel_pose['curr_frame']},")
                f.write(f"{rel_pose['position'].x},{rel_pose['position'].y},{rel_pose['position'].z},")
                f.write(f"{rel_q.w},{rel_q.x},{rel_q.y},{rel_q.z}\n")
    
    # Save IMU data for IMU-only and Visual-Inertial datasets
    for dir_path in [imu_dir, vi_dir]:
        with open(os.path.join(dir_path, "imu_data.txt"), 'w') as f:
            f.write("timestamp,acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z\n")
            for i in range(len(times)):
                f.write(f"{times[i]},{accel_data[i][0]},{accel_data[i][1]},{accel_data[i][2]},")
                f.write(f"{gyro_data[i][0]},{gyro_data[i][1]},{gyro_data[i][2]}\n")
    
    # Create a dataset-specific file to map IMU records to image pairs
    for dir_path in [imu_dir, vi_dir]:
        with open(os.path.join(dir_path, "imu_image_mapping.txt"), 'w') as f:
            f.write("prev_frame,curr_frame,start_imu_idx,end_imu_idx\n")
            for i in range(1, len(positions) // camera_interval):
                prev_frame = i - 1
                curr_frame = i
                start_imu_idx = prev_frame * camera_interval
                end_imu_idx = curr_frame * camera_interval
                f.write(f"{prev_frame},{curr_frame},{start_imu_idx},{end_imu_idx}\n")
    
    # Render images for vision-only and visual-inertial datasets
    print_log(f"Rendering {len(positions) // camera_interval} images")
    for i in range(0, len(positions), camera_interval):
        frame_idx = i // camera_interval
        
        # Update camera position and orientation
        camera.location = positions[i]
#        camera.rotation_euler = orientations[i]
        base_down = Euler((math.radians(90), 0, 0), 'XYZ')
        body      = Euler(orientations[i], 'XYZ')
        camera.rotation_euler = (base_down.to_matrix() @ body.to_matrix()).to_euler()
        
        # Set render path for both vision-only and visual-inertial directories
        for dir_path in [vis_dir, vi_dir]:
            image_path = os.path.join(dir_path, "images", f"frame_{frame_idx:04d}.png")
            bpy.context.scene.render.filepath = image_path
            
            # Only render every 5th frame during development to speed things up
            # Change to render every frame for final dataset
            if frame_idx % 1 == 0: #or frame_idx < 10:
                print_log(f"Rendering frame {frame_idx}/{len(positions) // camera_interval}")
                bpy.ops.render.render(write_still=True)
    
    print_log(f"Dataset generation complete for {trajectory_type}")
    return base_dir

def main():
    print_log("Starting synthetic data generation")
    
    # Define speeds (in m/s)
#    speeds = [1.0]#2.0, 3.0
    
    # Generate datasets - use a smaller number of points for testing
    num_points = 500  # Reduced for faster processing
    
    # Generate training datasets
    for trajectory in TRAIN_TRAJECTORIES:
#        for speed in speeds:
#            generate_dataset(trajectory, speed, OUTPUT_DIR, is_training=True, num_points=num_points)
            generate_dataset(trajectory, OUTPUT_DIR, is_training=True)
    
    # Generate testing datasets
    for trajectory in TEST_TRAJECTORIES:
#        for speed in speeds:
#            generate_dataset(trajectory, speed, OUTPUT_DIR, is_training=False, num_points=num_points)
             generate_dataset(trajectory, OUTPUT_DIR, is_training=False)

    
    print_log("All datasets generated successfully")

if __name__ == "__main__":
    bpy.ops.wm.save_mainfile(filepath=bpy.data.filepath)
    main()

