attribute vec2 coord2d;

void main(void) {
	gl_Position = vec4(coord2d, 0.0, 1.0);
	gl_Position.x = gl_Position.x / 320.0 - 1.0;
	gl_Position.y = -gl_Position.y / 240.0 + 1.0;
}