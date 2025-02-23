from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

import using.keyboards as kb
import config

import transport.parsing as prs

from aiogram.fsm.state import StatesGroup, State

router = Router()
choose = -1
last_route = ''

class ScheduleChoose(StatesGroup):
    route = State()
    stop_name = State()

class BackwardRoute(StatesGroup):
    route = State()
    check = State()

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет!\nЯ - Бот TimeToGo и я очень хочу защитить тебя от опозданий "
                         "по причине задерживающегося городского транспорта!\n\n Вот, что я умею", reply_markup=await kb.abilities())

@router.message(Command("stop"))
async def stop(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Все действия были отменены, а вы возвращены в меню!",
                         reply_markup=await kb.abilities())

@router.message(F.text == "Расписание")
@router.message(F.text == "Список остановок")
async def schedule_input_start(message : types.Message, state: FSMContext):
    print(f"Получено сообщение: {message.text}")
    global choose
    choose = kb.abilities_arr.index(message.text)
    await state.set_state(ScheduleChoose.route)
    await message.answer("Введите номер маршрута, который вам нужен!", reply_markup=ReplyKeyboardRemove())

@router.message(ScheduleChoose.route)
async def schedule_input_route(message: types.Message, state: FSMContext):
    global choose
    await state.update_data(route=message.text)
    await state.set_state(ScheduleChoose.stop_name)
    if choose != 3:
        await message.answer('Укажите точное название вашей остановки', reply_markup=kb.get_checkpoints)
    else:
        await state.update_data(stop_name="")
        data = await state.get_data()
        await state.clear()
        await checkpoints_list_output(message, data['route'], state)

@router.message(ScheduleChoose.stop_name)
async def schedule_input_name(message: types.Message, state: FSMContext):
    if message.text == 'Показать список остановок':
        data = await state.get_data()
        await checkpoints_list_output(message, data['route'], state)
    elif message.text == 'Показать список остановок (обратный рейс)':
        data = await state.get_data()
        await checkpoints_list_output(message, data['route'], state, 1)
    else:
        await state.update_data(stop_name=message.text)
        data = await state.get_data()
        await schedule_input_result(message, data)
        await state.clear()

async def checkpoints_list_output(message: types.Message, route: str, state: FSMContext, direction=0):
    loading_message = await message.answer_animation('https://media1.tenor.com/m/byY2-DioMQ4AAAAd/quirky-clown-bread-join-voice-call-vc.gif',caption='Пожалуйста, подождите пока я соберу информацию...')
    checkpoints = prs.Checkpoints(route=route, direction=direction).parse_checkpoints()
    checks_str = '\n'
    for check in checkpoints:
        if check != '':
            checks_str += f'🚏 `{check}` \n\n'
    await loading_message.delete()
    await message.answer(f'🚍 Вот всё, что я смог найти по актуальному списку остановок для маршрута {route}:\n{checks_str} \nНажмите на название, если Вам нужно его скопировать', parse_mode="MarkdownV2")
    if (await state.get_state()) is not None:
        answer = None
        if direction == 0:
            answer = kb.get_checkpoints_back
        else:
            answer = ReplyKeyboardRemove()
        await message.answer('А теперь укажите точное название вашей остановки', reply_markup=answer)
    else:
        if direction == 0:
            global last_route
            last_route = route
            await message.answer('Что-то ещё?', reply_markup=kb.get_checkpoints_back_plus)
        else:
            await message.answer('Что-то ещё?', reply_markup=await kb.abilities())

@router.message(F.text == 'Обратный рейс')
async def backward_list_checking(message: types.Message, state: FSMContext):
    global last_route
    if last_route != '':
        await checkpoints_list_output(message, last_route, state, direction=1)

async def schedule_input_result(message: types.Message, data):
    global choose
    route = data['route']
    stop_name = data['stop_name']

    if choose == 0:
        await message.answer("недоделано;(")
    elif choose == 1:
        await message.answer("недоделано;(")
    elif choose == 2:
        await entire_schedule_output(message, route, stop_name)
    else:
        await message.answer("Неизвестная ошибка. Попробуйте позже!")
    choose = 0

async def entire_schedule_output(message: types.Message, route: str, stop_name: str):
    loading_message = await message.answer_animation('https://media1.tenor.com/m/byY2-DioMQ4AAAAd/quirky-clown-bread-join-voice-call-vc.gif',caption='Пожалуйста, подождите пока я соберу информацию...')
    schedule_items = prs.Schedule(route=route, stop_name=stop_name, time_sleep=config.PARSER_TIME_SLEEP).parse_schedule()
    schedule_str = ''
    i = 0
    for item in schedule_items:
        if isinstance(item, str):
            await loading_message.delete()
            await user_error_report(message, item)
            return
        else:
            #if (not(item.isPassed())) or (not(schedule_items[i+1].isPassed())):
            schedule_str += item.getMessage() + "\n\n"
            i+=1

    await loading_message.delete()
    await message.answer(f'🚍 Вот всё, что я смог найти по сегодняшнему расписанию автобусов маршрута {route} относительно остановки {stop_name}: \n{schedule_str}', reply_markup=await kb.abilities())

async def user_error_report(message: types.Message, report : str):
    await message.answer_animation("https://media1.tenor.com/m/xJQzFjwewOkAAAAC/cat-gato.gif",
                                   caption=f'🚫 Возникла ошибка! \n\n{report}')
