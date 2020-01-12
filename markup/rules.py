class Rule:
    def action(self, block, handler):
        handler.start(self.type)
        handler.feed(block)
        handler.end(self.type)
        return True


class HeadingRule(Rule):
    """标题最多70字，不以冒号结束"""
    type = 'heading'

    def condition(self, block):
        return '\n' not in block and len(block) <= 70 and block[-1] != ':'


class TitleRule(HeadingRule):
    """题目是第一个块，作为标题"""
    type = 'title'
    first = True

    def condition(self, block):
        if not self.first:
            return False
        self.first = False
        return HeadingRule.condition(self, block)


class ListItemRule(Rule):
    """列表以连字符为开始的段落，然后连字符会被删除"""
    type = 'listitem'

    def condition(self, block):
        return block[0] == '-'

    def action(self, block, handler):
        handler.start(self.type)
        handler.feed(block[1:].strip())
        handler.end(self.type)
        return True


class ListRule(ListItemRule):
    """列表开始于非列表项的块和之后的列表项之间，由最后的连续列表项作为结束"""
    type = 'list'
    inside = False

    def condition(self, block):
        return True

    def action(self, block, handler):
        if not self.inside and ListItemRule.condition(self, block):
            handler.start(self.type)
            self.inside = True
        elif self.inside and not ListItemRule.condition(self, block):
            handler.end(self.type)
            self.inside = False
        return False


class ParagraphRule(Rule):
    """段落是不符合其他规则的块"""
    type = 'paragraph'

    def condition(self, block):
        return True
