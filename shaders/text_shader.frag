
uniform sampler2D tex;


float edge_thick = 0.01;
float edge_pos = 0.5;
float border_start = 0.07;
float border_end = 0.5;
float border_pos = edge_pos - border_start;


float aastep( float threshold, float distance) {
    float d  = (distance - threshold); // distance rebias 0..1 --> -0.5 .. +0.5
    float aa = 0.75*length( vec2( dFdx( d ), dFdy( d ))); // anti-alias
    return smoothstep( -aa, aa, d );
}
//float distance = texture2D( tex1, uv ).a;
//float alpha = aastep( 0.5, distance );


void main(void)
{
    vec4 color;
    color = texture2D(tex, gl_TexCoord[0].st);   
    color.a = smoothstep(color.b, border_pos-edge_thick, border_pos);
    color.a = color.a * float(color.b>border_pos);
    float edge = smoothstep(color.b,border_pos,border_end);
    
    float glow = 0.0;// 1.0-smoothstep(color.b, 0.4, 0.5);
    color.r = edge;
    color.g = edge - glow;
    color.b = edge;
    color.a = 0.85*color.a + 0.15*glow;
    
    gl_FragColor = color; 
}