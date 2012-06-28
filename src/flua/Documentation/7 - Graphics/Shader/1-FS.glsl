varying vec2 f_texcoord;
uniform vec4 f_color;
uniform sampler2D mytexture;

void main(void) {
	//vec2 flipped_texcoord = vec2(f_texcoord.x, 1.0 - f_texcoord.y);
	gl_FragColor = texture2D(mytexture, f_texcoord) * f_color;
	//gl_FragColor = vec4(f_texcoord, 0.0, 1.0);
}