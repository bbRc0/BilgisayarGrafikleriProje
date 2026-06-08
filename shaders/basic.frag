#version 330 core

in vec3 vWorldPos;
in vec3 vNormal;
in vec2 vTexCoord;

out vec4 FragColor;

uniform sampler2D uTexture;

// Yönlü ışık (örn. güneş). uLightDir, ışığın gittiği yön (ışıktan yüzeye doğru).
uniform vec3 uLightDir;
uniform vec3 uLightColor;
uniform vec3 uAmbient;

// Kamera/oyuncu pozisyonu (specular için bakış yönü hesabında kullanılır)
uniform vec3 uViewPos;

// Yüzey parlaklık üssü (büyük = küçük ve sert parlama, küçük = geniş ve yumuşak)
uniform float uShininess;
// Specular bileşeninin gücü
uniform float uSpecularStrength;

// 1.0 → aydınlatma bypass, texture rengini direkt göster (UI / overlay için)
uniform float uUnlit;

void main()
{
    vec3 texColor = texture(uTexture, vTexCoord).rgb;

    if (uUnlit > 0.5) {
        FragColor = vec4(texColor, 1.0);
        return;
    }

    vec3 N = normalize(vNormal);
    vec3 L = normalize(-uLightDir);          // yüzeyden ışık kaynağına doğru vektör
    vec3 V = normalize(uViewPos - vWorldPos); // yüzeyden kameraya
    vec3 H = normalize(L + V);                // halfway vector (Blinn-Phong)

    float diff = max(dot(N, L), 0.0);
    float spec = pow(max(dot(N, H), 0.0), uShininess);

    vec3 ambient  = uAmbient * texColor;
    vec3 diffuse  = diff * uLightColor * texColor;
    vec3 specular = uSpecularStrength * spec * uLightColor;

    FragColor = vec4(ambient + diffuse + specular, 1.0);
}
