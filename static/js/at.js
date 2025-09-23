var maildivider = "__SMAP__TA__DETELE__EM__";

for (i = 0; i <= (document.links.length - 1); i++) {
    if (document.links[i].href.indexOf(maildivider) != -1)
        document.links[i].href = document.links[i].href.split(maildivider)[0] + "@" + document.links[i].href.split(maildivider)[1]
}