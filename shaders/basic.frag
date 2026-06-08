#version 330 core

in vec3 vNormal;
in vec2 vTexCoord;

out vec4 FragColor;

uniform vec3 uColor;

void main()
{
    // Geçici sahte aydınlatma: yüzeyin yönüne göre hafif tonlama.
    // Phong aydınlatma adımında bu kısım gerçek ışıkla değiştirilecek.
    vec3 lightDir = normalize(vec3(0.4, 1.0, 0.6));
    float diff = max(dot(normalize(vNormal), lightDir), 0.0);
    float shade = 0.3 + 0.7 * diff;
    FragColor = vec4(uColor * shade, 1.0);
}
