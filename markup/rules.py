class Rule:
    type: str

    def action(self, block, handler):
        handler.start(self.type)
        handler.feed(block)
        handler.end(self.type)
        return True


class HeadingRule(Rule):
    type: str = "heading"

    @staticmethod
    def condition(block):
        return "\n" not in block and len(block) <= 70 and block[-1] != ":"


class TitleRule(HeadingRule):
    type: str = "title"
    first: bool = True

    def condition(self, block):
        if not self.first:
            return False
        self.first = False

        return HeadingRule.condition(block)


class ListItemRule(Rule):
    type: str = "listitem"

    @staticmethod
    def condition(block):
        return block[0] == "-"

    def action(self, block, handler):
        handler.start(self.type)
        handler.feed(block[1:].strip())
        handler.end(self.type)
        return True


class ListRule(ListItemRule):
    type: str = "list"
    inside: bool = False

    @staticmethod
    def condition():
        return True

    def action(self, block, handler):
        if not self.inside and ListItemRule.condition(self, block):
            handler.start(self.type)
            self.inside = True
        elif self.inside and not ListItemRule.condition(block):
            handler.end(self.type)
            self.inside = False

        return False


class ParagraphRule(Rule):
    type: str = "paragraph"

    @staticmethod
    def condition():
        return True
