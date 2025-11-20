//***** STRUCTURES *********************************************************************************
struct VertexInput {
    @builtin(vertex_index) vertex_index: u32,
};

struct VertexOutput {
    @location(0) color: vec4<f32>,
    @builtin(position) pos: vec4<f32>,
};
//***** STRUCTURES *********************************************************************************


//***** VERTEX SHADER ******************************************************************************
@vertex
fn vs_main(in: VertexInput) -> VertexOutput {
    // Define Triangle position directly here:
    var positions = array<vec2<f32>, 3>(
        vec2<f32>( 0.0, -0.5),
        vec2<f32>( 0.5,  0.5),
        vec2<f32>(-0.5,  0.5),
    );

    // Vertex colors:
    var colors = array<vec3<f32>, 3>(
        vec3<f32>(1.0, 0.0, 0.0), // RED
        vec3<f32>(0.0, 1.0, 0.0), // GREEN
        vec3<f32>(0.0, 0.0, 1.0), // BLUE
    );

    let index = i32(in.vertex_index);
    var out: VertexOutput;
    out.pos = vec4<f32>(positions[index], 0.0, 1.0);
    out.color = vec4<f32>(colors[index], 1.0);
    return out;
}
//***** VERTEX SHADER ******************************************************************************


//***** FRAGMENT SHADER ****************************************************************************
@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    // Gamma correction:
    let physical_color = pow(in.color.rgb, vec3<f32>(2.2));
    return vec4<f32>(physical_color, in.color.a);
}
//***** FRAGMENT SHADER ****************************************************************************
