Shader "EndlessSavagery/OrbitGlow"
{
    Properties { [HDR] _Tint ("Tint", Color) = (0.55,0.15,1,1) }
    SubShader
    {
        Tags { "Queue"="Transparent" "RenderType"="Transparent" }
        Blend SrcAlpha One
        ZWrite Off
        Cull Off
        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            float4 _Tint;
            struct Input { float4 vertex:POSITION; float4 color:COLOR; };
            struct Output { float4 position:SV_POSITION; float4 color:COLOR; };
            Output vert(Input v) { Output o; o.position=UnityObjectToClipPos(v.vertex); o.color=v.color*_Tint; return o; }
            fixed4 frag(Output i):SV_Target { return i.color; }
            ENDCG
        }
    }
}
