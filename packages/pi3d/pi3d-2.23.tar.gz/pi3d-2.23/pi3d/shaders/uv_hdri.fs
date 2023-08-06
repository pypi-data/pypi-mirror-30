#include std_head_fs.inc

varying vec2 texcoordout;
varying vec2 bumpcoordout;
varying vec3 inray;
varying vec3 normout;
varying vec3 lightVector;
varying float lightFactor;

vec2 make_coord(vec3 ray) {
  return vec2(atan(-ray.x, -ray.z) / 6.2831854 + 0.5, acos(ray.y) / 3.1415927);
}

void main(void) {
#include std_main_uv.inc
  vec3 bump = normalize(texture2D(tex1, bumpcoordout).rgb * 2.0 - 1.0);
  bump.y *= -1.0;
  // unib[3][2] ([11] in python) is used to adjust the strength of normal map textures
  float bfact = unib[3][2] * (1.0 - smoothstep(100.0, 600.0, dist)); // ------ attenuate smoothly between 100 and 600 units

  bump = normout - 0.1 * bfact * bump;
  vec3 refl = normalize(reflect(inray, bump)); // ----- reflection direction from this vertex
  vec2 shinecoord = make_coord(refl); // ------ potentially need to clamp with bump included in normal
  vec4 shinec = texture2D(tex2, shinecoord); // ------ get the reflection for this pixel
  vec2 hdricoord = make_coord(bump);
  vec4 hdri_val = texture2D(tex2, hdricoord, 6.0); // ------ light shining onto this pixel

  texc.rgb *= hdri_val.rgb * 1.5;

  float shinefact = clamp(unib[0][1]*length(shinec)/length(texc), 0.0, unib[0][1]);// ------ reduce the reflection where the ground texture is lighter than it

  gl_FragColor = (1.0 - ffact) * ((1.0 - shinefact) * texc + shinefact * shinec) + ffact * vec4(unif[4], unif[5][1]); // ------ combine using factors
  gl_FragColor.a *= unif[5][2];
}


