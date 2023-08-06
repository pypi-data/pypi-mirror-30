# 斗地主引擎

枚举了37种细分牌型，制作一个花色无关、顺序无关的字典，能够在O(1)时间内判断出牌是否有效，在O(1)时间内比较大小

扑克出牌是54张牌的组合，牌型和排列顺序无关，在斗地主游戏中除了两个王，花色也无关大小。

[详细文档](docs/engine.md)

## Quickstart

### Installing

- git clone https://github.com/onestraw/doudizhu
- cd doudizhu

### 开始一局游戏
```python
>>> import doudizhu
>>> from doudizhu import Card
>>> cards_groups = doudizhu.new_game()
>>>
>>> cards_groups
[[13, 32, 36, 43, 140, 21, 138, 42, 37, 131, 129, 16, 17, 26, 76, 70, 71], [27, 130, 67, 65, 35, 72, 69, 75, 33, 34, 68, 66, 135, 24, 134, 19, 25], [136, 20, 38, 28, 22, 23, 74, 73, 14, 44, 39, 133, 40, 132, 128, 18, 137], [64, 41, 139]]
>>>
>>> for cards_group in cards_groups:
...     Card.print_pretty_cards(cards_group)
...
  [ BJ  ] , [ 3 ❤ ] , [ 7 ❤ ] , [ A ❤ ] , [ 2 ♣ ] , [ 8 ♠ ] , [ K ♣ ] , [ K ❤ ] , [ 8 ❤ ] , [ 6 ♣ ] , [ 4 ♣ ] , [ 3 ♠ ] , [ 4 ♠ ] , [ K ♠ ] , [ 2 ♦ ] , [ 9 ♦ ] , [ 10 ♦ ]
  [ A ♠ ] , [ 5 ♣ ] , [ 6 ♦ ] , [ 4 ♦ ] , [ 6 ❤ ] , [ J ♦ ] , [ 8 ♦ ] , [ A ♦ ] , [ 4 ❤ ] , [ 5 ❤ ] , [ 7 ♦ ] , [ 5 ♦ ] , [ 10 ♣ ] , [ J ♠ ] , [ 9 ♣ ] , [ 6 ♠ ] , [ Q ♠ ]
  [ J ♣ ] , [ 7 ♠ ] , [ 9 ❤ ] , [ 2 ♠ ] , [ 9 ♠ ] , [ 10 ♠ ] , [ K ♦ ] , [ Q ♦ ] , [ CJ  ] , [ 2 ❤ ] , [ 10 ❤ ] , [ 8 ♣ ] , [ J ❤ ] , [ 7 ♣ ] , [ 3 ♣ ] , [ 5 ♠ ] , [ Q ♣ ]
  [ 3 ♦ ] , [ Q ❤ ] , [ A ♣ ]
```

### 检查牌型
```python
>>> test_chain = [Card.new('3c'), Card.new('4d'), Card.new('5h'), Card.new('6s'), Card.new('7s'), Card.new('8h')]
>>>
>>> test_four_two = [Card.new('2c'), Card.new('2d'), Card.new('2h'), Card.new('2s'), Card.new('BJ'), Card.new('CJ')]
>>>
>>> print doudizhu.check_card_type(test_four_two)
(True, [('four_two_solo', 13)])
>>> print doudizhu.check_card_type(test_chain)
(True, [('solo_chain_6', 0)])
>>> print doudizhu.check_card_type(test_chain[:4])
(False, ValueError('invalid card type',))
```

### 比较大小
```python
>>> chain = [Card.new('3c'), Card.new('4d'), Card.new('5h'), Card.new('6s'), Card.new('7s'), Card.new('8h'), Card.new('9h')]
>>> bomb = [Card.new('8h'), Card.new('8s'), Card.new('8d'), Card.new('8c')]
>>> rocket = [Card.new('BJ'), Card.new('CJ')]
>>>
>>> print doudizhu.cards_greater(chain, chain)
(False, 'solo_chain_7')
>>> print doudizhu.cards_greater(chain[:6], chain[1:7])
(False, 'solo_chain_6')
>>>
>>> print doudizhu.cards_greater(chain[1:7], chain[:6])
(True, 'solo_chain_6')
>>> print doudizhu.cards_greater(bomb, chain)
(True, 'bomb')
>>> print doudizhu.cards_greater(rocket, bomb)
(True, 'rocket')
```
