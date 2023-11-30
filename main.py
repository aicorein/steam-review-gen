import os
import re
from typing import Any, Union

import toml
import pyperclip
from rich import print


class ReviewGen:
    def __init__(self) -> None:
        self.options: list = []

    def refresh_screen(self):
        os.system('cls' if os.name=='nt' else 'clear')
        print("*************************************************")
        print(f"*********** Steam 评论生成器 1.0.0 **************")
        print("*************************************************")
        print()

    def get_idx(self, s: str) -> int:
        try:
            matched = re.search(r"-?[0-9]\d*(\.\d+)?", s)
            if matched == None:
                return None
            l, r = matched.regs[0][0], matched.regs[0][1]
            return int(s[l:r])-1
        except Exception:
            return None

    def load_options(self) -> None:
        files = filter(lambda x: x.endswith('.toml'), os.listdir('options'))
        for file in files:
            with open(os.path.join('options', file), 'r', encoding='utf-8') as fp:
                self.options.append(toml.load(fp))
    
    def choose_option(self) -> list:

        def show_page(again_flag: bool=False) -> Union[int, None]:
            self.refresh_screen()
            print("选择要使用的配置：")
            print()
            for i, name in enumerate([option['global']['name'] for option in self.options]):
                print(f"    {i+1}. {name}")
            print()
            if again_flag:
                print("[red]序号不合法，请重新输入序号：[/]", end='')
            else:
                print("输入序号确认：", end='')
            idx = self.get_idx(input())
            if idx == None or idx < 0 or idx >= len(self.options):
                idx = show_page(again_flag=True)
            return idx

        if len(self.options) > 1:
            idx = show_page()
            return self.options[idx]
        elif len(self.options) > 0:
            return self.options[-1]
        else:
            print("未检测到可用配置，即将退出")
            exit(0)

    def item_review(self, option: list) -> list:

        def show_page(content: dict, again_flag: bool=False) -> Union[int, None]:
            self.refresh_screen()
            print(f"你对【{content['display']}】的评价是：")
            print()
            for i, choice in enumerate(content['choices']):
                print(f"    {i+1}. {choice}")
            print()
            if again_flag:
                print("[red]序号不合法，请重新输入序号：[/]", end='')
            else:
                print("输入序号确认：", end='')
            idx = self.get_idx(input())
            if idx == None or idx < 0 or idx >= len(content['choices']):
                idx = show_page(content, again_flag=True)
            return idx

        result = {}
        for id, content in option['items'].items():
            idx = show_page(content)
            result[content['display']] = content['choices'][idx]
        return result

    def result_print(self, option: list, result: list) -> None:
        self.refresh_screen()
        print("生成的评价如下：（已复制到剪贴板）")
        id_format = option['global']['id_format']
        chosed_format = option['global']['choice_format']
        sep = option['global']['item_sep']
        output = ''
        for name, chosed in result.items():
            output += f"{id_format}{chosed_format}" %(name, chosed) + sep
        print(output)
        output += '\n（此评价由[url=github.com/AiCorein/steam-review-gen]Steam 评论生成器[/url]生成）'
        pyperclip.copy(output)
    
    def main(self) -> None:
        self.load_options()
        option = self.choose_option()
        result = self.item_review(option)
        self.result_print(option, result)


if __name__ == "__main__":
    try:
        ReviewGen().main()
    except KeyboardInterrupt:
        print()
        print()
        print("Ctrl-C 程序终止")
