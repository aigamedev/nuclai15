// View and edit online here:
// https://www.shadertoy.com/view/XlfSzB

const vec3 fog_color = vec3(0.7,0.85,1.0);
const float fog_density = 0.02;

//-------------------------------------------------------------------------
// MAP
//
// The cave structure is represented algorithmically as a signed
// distance field:
//      - positive numbers mean empty space
//      - negative numbers are solid space
//
// This distance is returned as the .x component of a 2D vector, and
// the .y component represents an optional texture "number".
//-------------------------------------------------------------------------
vec2 map( in vec3 pos )
{
    // ---- CEILING ----

    float ceiling_y =
        // global offset upwards of ceeling
        0.1
        // curve minimum around origin and slopes down
        +1.0 - 0.25 * sqrt(pos.x*pos.x + pos.z*pos.z)
	;
    
   	// ---- FLOOR ----
           
    float floor_y =
        // global offset downwards of floor
        0.6
        // curve minimum around origin and slopes upward
        +1.0 - 0.25 * sqrt(pos.x*pos.x + pos.z*pos.z)
    ;

    // The cave is made up of two planes with variable offsets.  
    return vec2( min(pos.y + floor_y, -pos.y + ceiling_y), 0.0 );
}

//----------------------------------------------------------------------
// TEXTURE
//
// The texture of the cave is computed based on a 3D position, usually
// around the contour where the signed distance field is zero.  This
// function also takes the material returned from the map() function,
// and then computes a color as a 3D vector. 
//----------------------------------------------------------------------
vec3 texture( in vec3 pos, in float mat )
{    
    // Default texture for the cave. This is currently a checkerboard.
    float f = mod( floor(5.0*pos.z) + floor(5.0*pos.x), 2.0);
    return 0.2 + 0.1*f*vec3(1.0);
}

//----------------------------------------------------------------------
// RENDERING
//
// A form of ray marching is used to trace through the signed distance
// field, then perform simple physically-based lighting.
//
// NOTE: You shouldn't need to change this unless you need more advanced
// customizations of the rendering process (e.g. reflections).
//----------------------------------------------------------------------
vec3 calcNormal( in vec3 pos )
{
	vec3 eps = vec3( 0.001, 0.0, 0.0 );
	vec3 nor = vec3(
	    map(pos+eps.xyy).x - map(pos-eps.xyy).x,
	    map(pos+eps.yxy).x - map(pos-eps.yxy).x,
	    map(pos+eps.yyx).x - map(pos-eps.yyx).x );
	return normalize(nor);
}

float calcAO( in vec3 pos, in vec3 nor )
{
	float occ = 0.0;
    float sca = 1.0;
    for( int i=0; i<5; i++ )
    {
        float hr = 0.01 + 0.12*float(i)/4.0;
        vec3 aopos =  nor * hr + pos;
        float dd = map( aopos ).x;
        occ += -(dd-hr)*sca;
        sca *= 0.95;
    }
    return clamp( 1.0 - 3.0*occ, 0.0, 1.0 );    
}

vec2 castRay( in vec3 ro, in vec3 rd )
{
    float tmin = 0.1;
    float tmax = 12.0;
    float scale = 0.1;
	float precis = 0.0001;
    float t = tmin;
    float m = -1.0;
	vec2 last = vec2(0.0, 0.0);
    for( int i=0; i<500; i++ )
    {
	    vec2 res = map( ro+rd*t );
        if( abs(res.x)<precis || t>tmax ) break;
        if( res.x * last.x < 0.0 ) {
            scale *= 0.5;
        }
        else if (res.x > last.x) {
        	scale = min(0.1, scale * 2.0);
		}
        t += res.x * scale;
	    m = res.y;
        last = res;
    }

    if( t>tmax ) m=-1.0;
    return vec2( t, m );
}

vec3 render( in vec3 ro, in vec3 rd )
{ 
    vec3 col = vec3(0.8, 0.9, 1.0);
    vec2 res = castRay(ro,rd);
    float t = res.x;
	float m = res.y;

    if( m>-0.5 )
    {
        vec3 pos = ro + t*rd;
        vec3 nor = calcNormal( pos );
        vec3 ref = reflect( rd, nor );

        col = texture(pos, m);

        // Lighting calculations.  
        float occ = calcAO( pos, nor );
		vec3  lig = normalize( vec3(0.0, 1.0, 0.0) - pos );
		float amb = clamp( 0.5+0.5*nor.y, 0.0, 1.0 );
        float dif = clamp( dot( nor, lig ), 0.0, 1.0 );
        float bac = clamp( dot( nor, normalize(vec3(-lig.x,0.0,-lig.z))), 0.0, 1.0 )*clamp( 1.0-pos.y,0.0,1.0);
        float dom = smoothstep( -0.1, 0.1, ref.y );
        float fre = pow( clamp(1.0+dot(nor,rd),0.0,1.0), 2.0 );
		float spe = pow(clamp( dot( ref, lig ), 0.0, 1.0 ),16.0);

        // You can customize the weights and colors
        // for each of these lighting components. 
		vec3 brdf = vec3(0.0);
        brdf += 1.20*dif;
		brdf += 1.20*spe*dif;
        brdf += 0.30*amb*occ;
        brdf += 0.40*dom*occ;
        brdf += 0.30*bac*occ;
        brdf += 0.40*fre*occ;
		brdf += 0.02;
		col = col*brdf;

        // Fog calculation.
    	col = mix( col, fog_color, 1.0-exp( -fog_density*t*t ) );
    }

	return vec3( clamp(col,0.0,1.0) );
}

//----------------------------------------------------------------------
// MAIN
//----------------------------------------------------------------------
mat3 setCamera( in vec3 ro, in vec3 ta, float cr )
{
	vec3 cw = normalize(ta-ro);
	vec3 cp = vec3(sin(cr), cos(cr),0.0);
	vec3 cu = normalize( cross(cw,cp) );
	vec3 cv = normalize( cross(cu,cw) );
    return mat3( cu, cv, cw );
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
	vec2 q = fragCoord.xy/iResolution.xy;
    vec2 p = -1.0+2.0*q;
	p.x *= iResolution.x/iResolution.y;
    vec2 mo = iMouse.xy/iResolution.xy;

    // Camera origin and target. 
	float time = 15.0 + iGlobalTime;
	vec3 ro = vec3( -0.5+3.2*cos(0.1*time + 6.0*mo.x), mo.y-0.5, 0.5 + 3.2*sin(0.1*time + 6.0*mo.x) );
	vec3 ta = vec3( -0.5, -0.4, 0.5 );
    mat3 ca = setCamera( ro, ta, 0.0 );
    
    // Ray direction.
	vec3 rd = ca * normalize( vec3(p.xy,2.5) );

    // Render this pixel.
    vec3 col = render( ro, rd );
	col = pow( col, vec3(0.4545) );
    fragColor = vec4( col, 1.0 );
}
