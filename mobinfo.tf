/set warn_curly_re=off
; strip "@{n}" from the end of the encoded attr; after that, the only instance
; of @{ should be at the beginning of the line
/def -F -i -mregexp -t"^\(?[A-z].+$" monster_exp_substitution = \
    /let enc=$[substr(encode_attr({*}), 0, -4)] %;\
    /if (strstr(enc, "@{", 1) != -1) \
	/return%;\
    /endif%;\
    /if (strncmp("@{Cblack}", enc, 8) == 0) \
        /let mobcolor=BCrgb521%;\
    /elseif (strncmp("@{BCblack}", enc, 9) == 0) \
        /let mobcolor=BCrgb251%;\
    /else \
        /return%;\
    /endif %; \
    /let mobcolor=@{%mobcolor} %; \
    /substitute -p %mobcolor%{*} @{BCwhite}@{n} %; \
    /python_call mobinfo.addMonsterToRoom %{*}
