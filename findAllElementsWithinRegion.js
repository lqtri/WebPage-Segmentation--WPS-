function getElementsInRegion(x, y, width, height) {
    var elements = [],
        expando = +new Date,
        cx = x,
        cy = y,
        curEl;

    height = y + height;
    width = x + width;

    while ((cy += 5) < height) {
        cx = x;
        while (cx < width) {
            curEl = document.elementFromPoint(cx, cy);
            if ( curEl && !curEl[expando] ) {
                curEl[expando] = new Number(0);
                elements.push(curEl);
                cx += curEl.offsetWidth;
            } else {
                cx += 5;
            }
        }
    }
    return elements;
}