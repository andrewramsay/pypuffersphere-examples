varying vec4 color;
uniform float resolution;
uniform float rotate, tilt;
#define M_PI 3.1415926535897932384626433832795

// From https://gist.github.com/neilmendoza/4512992
mat4 rotationMatrix(vec3 axis, float angle)
{
    axis = normalize(axis);
    float s = sin(angle);
    float c = cos(angle);
    float oc = 1.0 - c;
    
    return mat4(oc * axis.x * axis.x + c,           oc * axis.x * axis.y - axis.z * s,  oc * axis.z * axis.x + axis.y * s,  0.0,
                oc * axis.x * axis.y + axis.z * s,  oc * axis.y * axis.y + c,           oc * axis.y * axis.z - axis.x * s,  0.0,
                oc * axis.z * axis.x - axis.y * s,  oc * axis.y * axis.z + axis.x * s,  oc * axis.z * axis.z + c,           0.0,
                0.0,                                0.0,                                0.0,                                1.0);
}

void main()
{   
	vec4 pos_3d, norm_pos;
    vec3 light_dir = normalize(vec3(-0.2, -0.5, -0.7));
	float lat, lon, x, y, w, r, z;
    color = gl_Color;
    vec4 quad_pos;

    vec4 pos = gl_ModelViewMatrix * gl_Vertex;

    //lon = atan2(pos.y, pos.x);
    //lat = acos(pos.z) - M_PI/2;
    //if(abs(lon)<0.3)
    //   rotate = 0;

    //if(lat>0)
    //   rotate = -rotate;

    quad_pos = pos;
    int quad_ix = gl_VertexID % 4;

    vec3 fwd = normalize(pos.xyz);
    vec3 up = normalize(normalize(pos.xyz)-vec3(0,0,1));
    vec3 right = cross(up, fwd);

    int q1 = quad_ix / 2;
    int q2 = ((quad_ix+1) % 4) / 2;
    float xoff = (q1-0.5) * 2;
    float yoff = (q2-0.5) * 2;

    float radius = length(pos.xyz);
    radius = clamp(radius,0.3,1);
    quad_pos.xyz += xoff * right * 0.01 / (0.01+sqrt(radius));
    quad_pos.xyz += yoff * up * 0.002;

    pos = quad_pos;


    //pos.x = mod(pos.x, 2.0)-1.0;
    //radius = length(pos.xyz);
    mat4 rotation = rotationMatrix(vec3(0,0,1), rotate*radius);
    mat4 rotation2 = rotationMatrix(vec3(1,0,0), tilt*radius);
    
    pos_3d =  rotation2 * rotation * pos;        
    pos_3d.w = 0;



    float br = color.r;

    vec4 normal4;
    normal4.xyz = gl_Normal;
    vec3 normal3 = (rotation * gl_ModelViewMatrix * normal4).xyz;
    float spec = 0.5 + 0.5 * dot(normalize(normal3.xyz), light_dir);
    float sigma = 0.005;
    float rspec = spec + 50*exp(-((1-spec)*(1-spec)) / (sigma*sigma));    
    br = 1;
    color = vec4(0.2, 0.4, 0.9, 1.0) * (rspec * spec+0.2);

    // convert to sphere space
    norm_pos = normalize(pos_3d);

    lat = acos(norm_pos.z) - M_PI/2;
    lon = atan2(norm_pos.y, norm_pos.x);

    //if(abs(lon)<0.3 && rotate!=0)
    //    color.a = 0;

    
    r = (M_PI/2-lat)/M_PI;      
    w = resolution/2.0;
    x = w + r * w * cos(lon);
    y = w - r*w*sin(lon);
     	
    if(r>0.9)
        color.a = 0;
    gl_Position = gl_ProjectionMatrix * vec4(x,y,0.001*min(radius,1.0),1);
}