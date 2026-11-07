// Minimal dynamic OpenGL 3.3 loader (Windows: opengl32 exports GL 1.1; everything else via wglGetProcAddress).
#pragma once
#ifdef _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <GL/gl.h>
#include <mmsystem.h>
#include <cstddef>
typedef ptrdiff_t GLsizeiptr_; typedef char GLchar_;
#define GL_ARRAY_BUFFER 0x8892
#define GL_ELEMENT_ARRAY_BUFFER 0x8893
#define GL_STATIC_DRAW 0x88E4
#define GL_DYNAMIC_DRAW 0x88E8
#define GL_FRAGMENT_SHADER 0x8B30
#define GL_VERTEX_SHADER 0x8B31
#define GL_COMPILE_STATUS 0x8B81
#define GL_LINK_STATUS 0x8B82
#define GL_TEXTURE0 0x84C0
#define GL_CLAMP_TO_EDGE 0x812F
#define GL_MULTISAMPLE 0x809D
#define ISEKAI_GL_FUNCS(X) \
  X(GLuint, CreateShader, (GLenum)) X(void, ShaderSource, (GLuint, GLsizei, const GLchar_* const*, const GLint*)) \
  X(void, CompileShader, (GLuint)) X(void, GetShaderiv, (GLuint, GLenum, GLint*)) X(void, GetShaderInfoLog, (GLuint, GLsizei, GLsizei*, GLchar_*)) \
  X(GLuint, CreateProgram, ()) X(void, AttachShader, (GLuint, GLuint)) X(void, LinkProgram, (GLuint)) X(void, GetProgramiv, (GLuint, GLenum, GLint*)) \
  X(void, GetProgramInfoLog, (GLuint, GLsizei, GLsizei*, GLchar_*)) X(void, UseProgram, (GLuint)) X(void, DeleteShader, (GLuint)) \
  X(GLint, GetUniformLocation, (GLuint, const GLchar_*)) X(void, Uniform1i, (GLint, GLint)) X(void, Uniform1f, (GLint, GLfloat)) \
  X(void, Uniform2f, (GLint, GLfloat, GLfloat)) X(void, Uniform3f, (GLint, GLfloat, GLfloat, GLfloat)) X(void, Uniform4f, (GLint, GLfloat, GLfloat, GLfloat, GLfloat)) \
  X(void, Uniform3fv, (GLint, GLsizei, const GLfloat*)) X(void, UniformMatrix4fv, (GLint, GLsizei, GLboolean, const GLfloat*)) \
  X(void, GenVertexArrays, (GLsizei, GLuint*)) X(void, BindVertexArray, (GLuint)) X(void, GenBuffers, (GLsizei, GLuint*)) \
  X(void, BindBuffer, (GLenum, GLuint)) X(void, BufferData, (GLenum, GLsizeiptr_, const void*, GLenum)) X(void, BufferSubData, (GLenum, GLsizeiptr_, GLsizeiptr_, const void*)) \
  X(void, EnableVertexAttribArray, (GLuint)) X(void, VertexAttribPointer, (GLuint, GLint, GLenum, GLboolean, GLsizei, const void*)) \
  X(void, ActiveTexture, (GLenum)) X(void, GenerateMipmap, (GLenum))
#define X(r, n, a) inline r (APIENTRY* gl##n) a = nullptr;
ISEKAI_GL_FUNCS(X)
#undef X
namespace isekai {
// Returns false (and names the first missing entry point) if any GL 3.3 function could not be resolved.
inline bool loadGLFunctions(const char** missing) {
  HMODULE lib = LoadLibraryA("opengl32.dll"); bool ok = true; *missing = nullptr;
  auto get = [&](const char* n) -> void* {
    void* p = (void*)wglGetProcAddress(n); auto v = (intptr_t)p;
    if (v == 0 || v == 1 || v == 2 || v == 3 || v == -1) p = lib ? (void*)GetProcAddress(lib, n) : nullptr; return p; };
#define X(r, n, a) if (!(gl##n = (decltype(gl##n))get("gl" #n))) { if (ok) *missing = "gl" #n; ok = false; }
  ISEKAI_GL_FUNCS(X)
#undef X
  return ok;
}
}  // namespace isekai
#endif
