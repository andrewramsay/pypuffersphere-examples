varying vec4 color;
uniform float resolution;
uniform float rotate;
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
    vec3 light_dir = normalize(vec3(0.2, -0.5, 0.5));
	float lat, lon, x, y, w, r, z;
    color = gl_Color;



    vec4 pos = gl_ModelViewMatrix * gl_Vertex;
    pos.x = mod(pos.x, 2.0)-1.0;
    float radius = length(pos.xyz);
    mat4 rotation = rotationMatrix(vec3(0,1,0), rotate*radius);
    pos_3d =  rotation * pos;        
    pos_3d.w = 0;

    float br = color.r;

    vec4 normal4;
    normal4.xyz = gl_Normal;
    vec3 normal3 = (gl_ModelViewMatrix * normal4).xyz;
    float spec = dot(normalize(normal3), light_dir);
    spec = exp(-log(1-spec)/8);
    gl_PointSize = min(spec,5);
    color = vec4(0.2, 0.4, 0.9, 1.0) * br * (exp(spec)+0.5);

    // convert to sphere space
    norm_pos = normalize(pos_3d);

    lat = acos(norm_pos.z) - M_PI/2;
    lon = atan2(norm_pos.y, norm_pos.x);
    
    r = (M_PI/2-lat)/M_PI;      
    w = resolution/2.0;
    x = w + r * w * cos(lon);
    y = w - r*w*sin(lon);
     	
    gl_Position = gl_ProjectionMatrix * vec4(x,y,0,1);
}