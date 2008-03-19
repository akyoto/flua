#include "Texture.hpp"

//Load
bool TOpenGLTexture::Load(Pixmap pixmap)
{
	width = pixmap->GetWidth();
	height = pixmap->GetHeight();
	
	Destroy();
	
	EngineLog4("Creating texture from pixmap: " << width << ", " << height << ", bpp: " << pixmap->GetBytesPerPixel() << ", format: " << pixmap->GetFormat());
	
	//glPixelStorei(GL_UNPACK_ALIGNMENT, 1);
	glGenTextures(1, &handle);
	glBindTexture(GL_TEXTURE_2D, handle);
	glPixelStorei(GL_UNPACK_ALIGNMENT, 4);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);//GL_CLAMP_TO_EDGE);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);//GL_CLAMP_TO_EDGE);
	gluBuild2DMipmaps(GL_TEXTURE_2D, pixmap->GetBytesPerPixel(), width, height, pixmap->GetFormat(), GL_UNSIGNED_BYTE, pixmap->GetData());
	
	//Calculate u/v
	//u0 = 0.0f;
	//v0 = 0.0f;
	//u1 = 1.0f;
	//v1 = 1.0f;
	
	GLenum error = glGetError();
	if(error != GL_NO_ERROR)
	{
		EngineLogErrorOGL("Can't create texture from pixmap", error);
		return 0;
	}
	
	return 1;
}

//DrawQueue
void TOpenGLTexture::DrawQueue()
{
	float x, y, z, endX, endY;
	
	glBindTexture(GL_TEXTURE_2D, handle);
	
	//Draw the queue
	vector<DrawImageCallInfo>::iterator theEnd = drawImageQueue.begin() - 1;
	glBegin(GL_QUADS);
	for(vector<DrawImageCallInfo>::iterator it = drawImageQueue.end() - 1; it != theEnd; --it)
	{
		x = it->x;
		y = it->y;
		z = it->z;
		endX = width - it->handleXY.x;
		endY = height - it->handleXY.y;
		
		if(it->rotationZ != currentRotationZ || it->scalingX != currentScalingX || it->scalingY != currentScalingY)
		{
			currentRotationZ = it->rotationZ;
			currentScalingX = it->scalingX;
			currentScalingY = it->scalingY;
			Update2DMatrix();
		}
		
		glColor4ub(it->r, it->g, it->b, it->a);
		
		glTexCoord2i(0, 0);
		glVertex3f(	-handleXY.x * cosScaleX - handleXY.y * sinScaleY + x,
					-handleXY.x * sinScaleX - handleXY.y * cosScaleY + y,
					z);
		
		glTexCoord2i(1, 0);
		glVertex3f(	endX * cosScaleX - handleXY.y * sinScaleY + x,
					endX * sinScaleX - handleXY.y * cosScaleY + y,
					z);
		
		glTexCoord2i(1, 1);
		glVertex3f(	endX * cosScaleX + endY * sinScaleY + x,
					endX * sinScaleX + endY * cosScaleY + y,
					z);
		
		glTexCoord2i(0, 1);
		glVertex3f(	-handleXY.x * cosScaleX + endY * sinScaleY + x,
					-handleXY.x * sinScaleX + endY * cosScaleY + y,
					z);
	}
	glEnd();
	drawImageQueue.clear();
}
