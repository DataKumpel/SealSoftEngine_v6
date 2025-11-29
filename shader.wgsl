//***** UNIFORMS ***********************************************************************************

// GROUP 0: Global Data (Camera)
struct CameraUniform {
    view: mat4x4<f32>,
    proj: mat4x4<f32>,
};

@group(0) @binding(0)
var<uniform> camera: CameraUniform;

// GROUP 1: Object Data (position and rotation of an object)
struct ModelUniform {
    matrix: mat4x4<f32>,
};

@group(1) @binding(0)
var<uniform> model: ModelUniform;

//***** UNIFORMS ***********************************************************************************

//***** STRUCTURES *********************************************************************************
struct VertexInput {
    @location(0) position: vec3<f32>,
    @location(1) color: vec3<f32>,
};

struct VertexOutput {
    @builtin(position) pos: vec4<f32>,
    @location(0) color: vec3<f32>,
};
//***** STRUCTURES *********************************************************************************


//***** VERTEX SHADER ******************************************************************************
@vertex
fn vs_main(in: VertexInput) -> VertexOutput {
    var out: VertexOutput;

    // MVP * pos = PROJ * VIEW * MODEL * POSITION
    out.pos = camera.proj * camera.view * model.matrix * vec4<f32>(in.position, 1.0);
    out.color = in.color;

    return out;
}
//***** VERTEX SHADER ******************************************************************************


//***** FRAGMENT SHADER ****************************************************************************
@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    // Gamma correction:
    let physical_color = pow(in.color, vec3<f32>(2.2));
    return vec4<f32>(physical_color, 1.0);
}
//***** FRAGMENT SHADER ****************************************************************************
