class IRCColors:
    white = "\x0300"
    black = "\x0301"
    blue = "\x0302"
    green = "\x0303"
    red = "\x0304"
    brown = "\x0305"
    purple = "\x0306"
    orange = "\x0307"
    yellow = "\x0308"
    light_green = "\x0309"
    teal = "\x0310"
    light_cyan = "\x0311"
    light_blue = "\x0312"
    pink = "\x0313"
    grey = "\x0314"
    light_grey = "\x0315"
    default = "\x0399"
    reset = "\x03"
    all = [white, black, blue, green, red, brown, purple, orange, yellow, light_green, teal, light_cyan, light_blue,
           pink, grey, light_grey, default, reset]


class IRCFormatting:
    bold = "\x02"
    italic = "\x1D"
    underline = "\x1F"
    reset = "\x0F"
    all = [bold, italic, underline, reset]
