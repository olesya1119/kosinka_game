import pygame
import random

# Инициализация Pygame
pygame.init()

# Размеры экрана
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
CARD_WIDTH = 100
CARD_HEIGHT = 140
FPS = 30

# Цвета
GREEN = (0, 128, 0)
WHITE = (255, 255, 255)

# Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Косынка")

# Загрузка изображений карт
def load_card_images():
    suits = ['clubs', 'diamonds', 'hearts', 'spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    card_images = {}
    for suit in suits:
        for rank in ranks:
            card = f"{suit}_{rank}"
            card_images[card] = pygame.image.load(f"cards/{card}.jpg")
    card_images['back'] = pygame.image.load("cards/back.jpg")  # Рубашка карты
    return card_images

card_images = load_card_images()

# Создание колоды
def create_deck():
    suits = ['clubs', 'diamonds', 'hearts', 'spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return [f"{suit}_{rank}" for suit in suits for rank in ranks]

# Получение масти и ранга карты
def get_card_info(card):
    suit, rank = card.split('_')
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['clubs', 'diamonds', 'hearts', 'spades']
    return suits.index(suit), ranks.index(rank)  # Возвращаем индекс масти и ранга

# Проверка, можно ли переместить карту в фонд
def can_move_to_foundation(card, foundation):
    """Проверяет, можно ли переместить карту в фонд"""
    if not foundation:  # Если фонд пуст, разрешается только двойка
        return get_card_info(card)[1] == 0  # Ранг двойки = 0
    suit, rank = get_card_info(card)
    foundation_suit, foundation_rank = get_card_info(foundation[-1])
    return suit == foundation_suit and rank == foundation_rank + 1  # Ранг на 1 больше, масть та же

# Проверка цвета масти
def get_card_color(card):
    suit, _ = card.split('_')
    if suit in ['hearts', 'diamonds']:
        return 'red'
    else:
        return 'black'

# Проверка на возможность перемещения карты
def can_place_on(card1, card2):
    """Проверяет, можно ли положить card1 на card2 (с учётом чередования цветов и убывания рангов)"""
    _, rank1 = get_card_info(card1)
    _, rank2 = get_card_info(card2)
    color1 = get_card_color(card1)
    color2 = get_card_color(card2)
    return rank1 + 1 == rank2 and color1 != color2  # Ранги уменьшаются, цвет чередуется

# Проверка, можно ли положить карту на пустую ячейку игровой зоны
def can_place_on_empty(card):
    """Проверяет, можно ли положить карту на пустую ячейку (только король)"""
    _, rank = get_card_info(card)
    return rank == 12  # Король имеет ранг 12

# Проверка, можно ли перетащить стопку карт
def can_move_stack(stack):
    """Проверяет, отсортирована ли стопка по убыванию"""
    for i in range(len(stack) - 1):
        if not can_place_on(stack[i + 1], stack[i]):
            return False
    return True

# Раздача карт
def deal_cards(deck):
    tableau = [[] for _ in range(7)]
    for i in range(7):
        for j in range(i + 1):
            tableau[i].append(deck.pop())
    return tableau

# Основная функция игры
def solitaire():
    clock = pygame.time.Clock()
    deck = create_deck()
    random.shuffle(deck)
    tableau = deal_cards(deck)
    foundations = [[] for _ in range(4)]  # Фонды для каждой масти
    stock = deck  # Запасная колода
    waste = []  # Отброс

    dragged_cards = None
    dragged_card_offset = (0, 0)
    selected_source = None  # Источник: "tableau" или "waste"
    last_click_time = 0
    double_click_threshold = 300  # Время для двойного клика (в миллисекундах)

    # Основной игровой цикл
    running = True
    while running:
        screen.fill(GREEN)

        # Отрисовка фундамента
        for i, foundation in enumerate(foundations):
            x = SCREEN_WIDTH - (4 - i) * (CARD_WIDTH + 10) - 50
            y = SCREEN_HEIGHT - CARD_HEIGHT - 20
            if foundation:
                screen.blit(card_images[foundation[-1]], (x, y))
            else:
                pygame.draw.rect(screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)

        # Отрисовка таблицы
        for i, column in enumerate(tableau):
            x = 50 + i * (CARD_WIDTH + 10)
            for j, card in enumerate(column):
                y = 150 + j * 20
                if dragged_cards and ("tableau", i, j) in dragged_cards:  # Не отрисовывать перетаскиваемые карты
                    continue
                screen.blit(card_images[card if j == len(column) - 1 or can_move_stack(column[j:]) else 'back'], (x, y))

        # Отрисовка запасной колоды
        if stock:
            screen.blit(card_images['back'], (50, 600))
        elif not stock and waste:  # Показать кнопку возврата карт в колоду
            pygame.draw.rect(screen, WHITE, (50, 600, CARD_WIDTH, CARD_HEIGHT), 2)

        if waste:
            screen.blit(card_images[waste[-1]], (160, 600))

        # Отрисовка перетаскиваемой стопки карт
        if dragged_cards:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for idx, (_, col_idx, card_idx) in enumerate(dragged_cards):
                if selected_source == "waste":
                    card = waste[-1]
                else:
                    card = tableau[col_idx][card_idx]
                screen.blit(card_images[card], (mouse_x - dragged_card_offset[0], mouse_y - dragged_card_offset[1] + idx * 20))

        # Обновление экрана
        pygame.display.flip()

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                current_time = pygame.time.get_ticks()
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Двойной клик для автоматического перемещения в фонд
                if current_time - last_click_time < double_click_threshold:
                    for i, column in enumerate(tableau):
                        x = 50 + i * (CARD_WIDTH + 10)
                        if x <= mouse_x <= x + CARD_WIDTH and column:
                            last_card = column[-1]
                            foundation_index = get_card_info(last_card)[0]
                            if can_move_to_foundation(last_card, foundations[foundation_index]):
                                foundations[foundation_index].append(column.pop())
                                break

                last_click_time = current_time

                # Клик по запасной колоде
                if 50 <= mouse_x <= 50 + CARD_WIDTH and 600 <= mouse_y <= 600 + CARD_HEIGHT:
                    if stock:
                        waste.append(stock.pop())
                    elif not stock and waste:  # Возврат карт в колоду
                        stock.extend(reversed(waste))
                        waste.clear()

                # Клик по отбросу
                if 160 <= mouse_x <= 160 + CARD_WIDTH and 600 <= mouse_y <= 600 + CARD_HEIGHT and waste:
                    dragged_cards = [("waste", 0, len(waste) - 1)]
                    dragged_card_offset = (mouse_x - 160, mouse_y - 600)
                    selected_source = "waste"

                # Клик по картам на столе
                for i, column in enumerate(tableau):
                    x = 50 + i * (CARD_WIDTH + 10)
                    for j, card in enumerate(column):
                        y = 150 + j * 20
                        if x <= mouse_x <= x + CARD_WIDTH and y <= mouse_y <= y + CARD_HEIGHT:
                            if can_move_stack(column[j:]):  # Проверяем, можно ли перетащить стопку
                                dragged_cards = [("tableau", i, k) for k in range(j, len(column))]
                                dragged_card_offset = (mouse_x - x, mouse_y - y)
                                selected_source = "tableau"
                                break
                    if dragged_cards:
                        break

            elif event.type == pygame.MOUSEBUTTONUP:
                if dragged_cards:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    target_column = None

                    # Попытка положить стопку в столбец
                    for i, column in enumerate(tableau):
                        x = 50 + i * (CARD_WIDTH + 10)
                        if x <= mouse_x <= x + CARD_WIDTH:
                            target_column = i
                            break

                    # Логика перемещения карт
                    if selected_source == "tableau":
                        if target_column is not None:
                            stack = [tableau[col_idx][card_idx] for _, col_idx, card_idx in dragged_cards]
                            if tableau[target_column]:
                                if can_place_on(stack[0], tableau[target_column][-1]):
                                    tableau[target_column].extend(stack)
                                    tableau[dragged_cards[0][1]][dragged_cards[0][2]:] = []
                            elif can_place_on_empty(stack[0]):  # Проверяем, что верхняя карта — король
                                tableau[target_column].extend(stack)
                                tableau[dragged_cards[0][1]][dragged_cards[0][2]:] = []

                    elif selected_source == "waste":
                        card = waste.pop()
                        foundation_index = get_card_info(card)[0]
                        if target_column is None and can_move_to_foundation(card, foundations[foundation_index]):
                            foundations[foundation_index].append(card)
                        elif target_column is not None and tableau[target_column] and can_place_on(card, tableau[target_column][-1]):
                            tableau[target_column].append(card)
                        elif target_column is not None and can_place_on_empty(card):  # Проверяем, что карта — король
                            tableau[target_column].append(card)
                        else:
                            waste.append(card)  # Вернуть карту в отброс, если она не подходит

                    dragged_cards = None

        clock.tick(FPS)

# Запуск игры
solitaire()
pygame.quit()

