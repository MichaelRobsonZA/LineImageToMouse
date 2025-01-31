import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

def calculate_timings(rpm):
    """Calculate timing details from RPM"""
    ms_per_shot = (60 / rpm) * 1000
    return {
        'ms_per_shot': ms_per_shot,
        'shots_per_second': rpm / 60
    }

def generate_curve_points(segments, curve_strengths, total_duration):
    """Generate smooth curve points for pattern preview"""
    points_per_segment = 50
    x, y = [], []
    time = np.linspace(0, total_duration, len(segments) * points_per_segment)
    
    # Generate base points
    for i, segment in enumerate(segments):
        t = np.linspace(0, 1, points_per_segment)
        curve_strength = curve_strengths[i]
        
        # Base movement
        x_move = segment['horizontal'] * t
        y_move = segment['vertical'] * t
        
        # Add curve effect
        if curve_strength != 0:
            curve = np.sin(t * np.pi) * curve_strength
            x_move += curve
            
        x.extend(x_move + (0 if i == 0 else x[-1]))
        y.extend(y_move + (0 if i == 0 else y[-1]))
    
    return x, y, time

def create_lua_script(segments, timings, curve_strengths, base_delay):
    """Generate Lua script with advanced pattern control"""
    script = """-- Auto-generated recoil control script
-- Weapon stats: 1091 RPM, 26.64°/s vertical, 28.47°/s horizontal

function OnEvent(event, arg)
    if event == "PROFILE_ACTIVATED" then
        EnablePrimaryMouseButtonEvents(true)
    end

    if event == "MOUSE_BUTTON_PRESSED" and arg == 1 and IsMouseButtonPressed(3) then
        local startTime = GetRunningTime()
        local shotCount = 0
        repeat
            local currentTime = GetRunningTime() - startTime\n"""
    
    total_time = 0
    for i, segment in enumerate(segments):
        time_start = total_time
        time_end = time_start + segment['duration']
        
        script += f"""            if currentTime >= {time_start} and currentTime < {time_end} then
                local segmentTime = currentTime - {time_start}
                local verticalStr = {segment['vertical']}
                local horizontalStr = {segment['horizontal']}
                """
        
        if curve_strengths[i] != 0:
            script += f"""                local curveEffect = math.sin(segmentTime / {segment['duration']} * math.pi) * {curve_strengths[i]}
                MoveMouseRelative(horizontalStr + curveEffect, verticalStr)
                """
        else:
            script += """                MoveMouseRelative(horizontalStr, verticalStr)
                """
            
        script += "            end\n"
        total_time += segment['duration']
    
    script += f"""            shotCount = shotCount + 1
            Sleep({base_delay})
        until not (IsMouseButtonPressed(1) and IsMouseButtonPressed(3)) or shotCount >= 60
    end
end"""
    
    return script

def main():
    st.title("Advanced Recoil Pattern Designer")
    
    # Weapon stats display
    st.sidebar.subheader("Weapon Statistics")
    rpm = st.sidebar.number_input("Fire Rate (RPM)", value=1091, min_value=300, max_value=1200)
    mag_size = st.sidebar.number_input("Magazine Size", value=60, min_value=1, max_value=100)
    
    timings = calculate_timings(rpm)
    st.sidebar.write(f"Time between shots: {timings['ms_per_shot']:.1f}ms")
    
    # Main pattern settings
    st.subheader("Pattern Segments")
    num_segments = st.slider("Number of segments", 2, 6, 3, 
                           help="Divide the recoil pattern into different phases")
    
    # Create containers for segment settings
    segments = []
    curve_strengths = []
    
    col1, col2 = st.columns(2)
    
    # Global settings
    with col1:
        st.subheader("Global Settings")
        base_delay = st.slider("Base Delay (ms)", 1, 30, 14,
                             help="Delay between movements")
        pattern_duration = st.slider("Pattern Duration (ms)", 500, 3000, 2000,
                                   help="Total duration of the pattern")
    
    # Segment-specific settings
    st.subheader("Segment Settings")
    for i in range(num_segments):
        st.write(f"Segment {i+1}")
        cols = st.columns(4)
        
        with cols[0]:
            vert = st.slider(f"Vertical #{i+1}", -10, 10, 
                           4 if i == 0 else max(1, 4-i),
                           help="Vertical recoil strength")
        
        with cols[1]:
            horiz = st.slider(f"Horizontal #{i+1}", -10, 10,
                            0 if i == 0 else min(-1, -1-i),
                            help="Horizontal recoil strength")
        
        with cols[2]:
            duration = st.slider(f"Duration #{i+1}", 100, 1000,
                               pattern_duration // num_segments,
                               help="Duration of this segment")
        
        with cols[3]:
            curve = st.slider(f"Curve #{i+1}", -5, 5, 0,
                            help="Curve intensity for this segment")
            
        segments.append({
            'vertical': vert,
            'horizontal': horiz,
            'duration': duration
        })
        curve_strengths.append(curve)
    
    # Pattern preview
    st.subheader("Pattern Preview")
    x, y, time = generate_curve_points(segments, curve_strengths, pattern_duration)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Movement pattern
    ax1.plot(x, y, 'b-', label='Movement Pattern')
    ax1.set_title("Recoil Pattern")
    ax1.set_xlabel("Horizontal Movement")
    ax1.set_ylabel("Vertical Movement")
    ax1.grid(True)
    
    # Time series
    ax2.plot(time, y, 'r-', label='Vertical')
    ax2.plot(time, x, 'b-', label='Horizontal')
    ax2.set_title("Movement Over Time")
    ax2.set_xlabel("Time (ms)")
    ax2.set_ylabel("Movement Strength")
    ax2.grid(True)
    ax2.legend()
    
    st.pyplot(fig)
    
    # Generate script button
    if st.button("Generate Lua Script"):
        script = create_lua_script(segments, timings, curve_strengths, base_delay)
        st.download_button(
            "Download Script",
            script,
            file_name="recoil_pattern.lua",
            mime="text/plain"
        )
        st.success("Script generated! Use LMB + RMB to activate the pattern.")

if __name__ == "__main__":
    main()