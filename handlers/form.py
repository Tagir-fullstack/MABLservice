from aiogram import Bot, F, Router
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from fsm.steps import AddData, EditData, FinishOrder, OrderHistory, ClientSteps, AddOldOrder
from config import ADMIN_ID, GROUP_ID
from keyboards.reply import reply_keyboard_status, reply_keyboard_end_order
from keyboards.inline import    inline_keyboard_start, inline_keyboard_edit_data, \
                                inline_keyboard_history, inline_keyboard_find_by_id, \
                                inline_keyboard_confirm_edit_data, inline_keyboard_verify_by, \
                                inline_keyboard_find_by_back
from utils.db_request import Request

router = Router()

@router.message(Command('id'))
async def id_cmd(message:Message, bot: Bot):
    await bot.send_message(message.chat.id, f'{message.from_user.id}')
    print(message.from_user.id)



@router.message(CommandStart())
async def start_cmd(message: Message, bot: Bot, state: FSMContext):
    # for mabl_id in MABL_IDS:
        if message.from_user.id == ADMIN_ID: #mabl_id
            await bot.send_message(chat_id=ADMIN_ID, #mabl_id
                                    text="Выберите действие",
                                    reply_markup=inline_keyboard_start())
        else:
            await message.answer(f'Введите номер заказа')
            await state.set_state(ClientSteps.GET_ID)


@router.callback_query(F.data == 'handler_to_main')
async def start_cmd_cb(call:CallbackQuery, state: FSMContext):
    await call.answer()
    # for mabl_id in MABL_IDS:
    if call.from_user.id == ADMIN_ID: #mabl_id
        await call.message.edit_text(text="Выберите действие",
                                     reply_markup=inline_keyboard_start())
    else:
        await call.message.edit_text(f'Введите номер заказа')
        await state.set_state(ClientSteps.GET_ID)



#######################################################################################################################


@router.message(StateFilter(ClientSteps.GET_ID))
async def client_id(message: Message, state: FSMContext, request: Request):
    await state.update_data(client_order_id=message.text)
    data = await state.get_data()
    order_id = data.get('client_order_id')
    id = await request.get_order(id=order_id)
    if id:
        await message.answer(
            f"Выберите метод верификации заказа",
            reply_markup=inline_keyboard_verify_by()
        )

    else:
        await message.answer(f"Заказ под таким номером не существует")



@router.callback_query(F.data == 'verify_by_name')
async def client_verify_by_name(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text(f'Введите ваши имя')
    await state.set_state(ClientSteps.GET_NAME)

@router.message(StateFilter(ClientSteps.GET_NAME))
async def client_name_v(message: Message, state: FSMContext, request: Request):
    await state.update_data(name=message.text)
    data = await state.get_data()
    order_id = data.get('client_order_id')
    client_name = data.get('name')
    id = await request.get_client_order_by_name(id=order_id, name=client_name)
    if id and client_name:
        await message.answer(
            f"Заказ:   <b>№{id['id']}</b> от {id['created_at']}\n"
            f"Имя:  <b>{id['name']}</b>\n"
            f"Устройство:    <b>{id['device']}</b>\n"
            f"Статус заказа:   <b>{id['status']}</b>\n"
        )
        await state.clear()

    else:
        await message.answer(f"Имя клиента не соответствует указанной в номере заказа. Попробуйте снова", reply_markup=inline_keyboard_verify_by())
        await state.clear()


@router.callback_query(F.data == 'verify_by_phone')
async def client_verify_by_phone(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text(f'Введите последние 5 цифр вашего мобильного номера')
    await state.set_state(ClientSteps.GET_PHONE)

@router.message(StateFilter(ClientSteps.GET_PHONE))
async def client_phone_v(message: Message, state: FSMContext, request: Request):
    await state.update_data(phone=message.text)
    data = await state.get_data()
    order_id = data.get('client_order_id')
    client_phone = data.get('phone')
    id = await request.get_client_order_by_phone(id=order_id, phone_suffix=client_phone)
    if id:
        await message.answer(
            f"Заказ:   <b>№{id['id']}</b> от {id['created_at']}\n"
            f"Имя:  <b>{id['name']}</b>\n"\
            f"Устройство:    <b>{id['device']}</b>\n"
            f"Статус заказа:   <b>{id['status']}</b>\n"
        )
        await state.clear()

    else:
        await message.answer(f"Номер телефона не соответствует указанной в номере заказа. Попробуйте снова", reply_markup=inline_keyboard_verify_by())
        await state.clear()


#######################################################################################################################



@router.callback_query(F.data == 'Create')
async def get_name(call: CallbackQuery, state: FSMContext, request: Request):
    await call.answer()
    next_id = await request.get_next_order_id()
    await call.message.answer(f'Вы создаете заказ под номером: <b>{next_id}</b>\n\nВведите имя клиента: ')
    await state.set_state(AddData.GET_NAME)


@router.message(StateFilter(AddData.GET_NAME))
async def get_phone(message: Message, state: FSMContext):
    await message.answer(text="Введите контактные данные клиента")
    await state.update_data(name=message.text)
    await state.set_state(AddData.GET_PHONE)


@router.message(StateFilter(AddData.GET_PHONE))
async def get_device(message: Message, state: FSMContext):
    await message.answer(text="Введите наименование устройства")
    await state.update_data(phone=message.text)

    await state.set_state(AddData.GET_DEVICE)

@router.message(StateFilter(AddData.GET_DEVICE))
async def get_problem(message: Message, state: FSMContext):
    await message.answer(text="Опишите проблему")
    await state.update_data(device=message.text)

    await state.set_state(AddData.GET_PROBLEM)

@router.message(StateFilter(AddData.GET_PROBLEM))
async def get_status(message: Message, state: FSMContext):
    await message.answer(text="Выберите статус заказа", reply_markup=reply_keyboard_status())
    await state.update_data(problem=message.text)

    await state.set_state(AddData.GET_STATUS)

@router.message(StateFilter(AddData.GET_STATUS))
async def get_comments(message: Message, state: FSMContext):
    await message.answer(text="Добавьте комментарий")
    await state.update_data(status=message.text)

    await state.set_state(AddData.GET_COMMENTS)


@router.message(StateFilter(AddData.GET_COMMENTS))
async def get_created_status(message: Message, bot: Bot, state: FSMContext, request: Request):
    await state.update_data(comment=message.text)
    user_data = await state.get_data()
    name = user_data.get('name')
    phone = user_data.get('phone')
    device = user_data.get('device')
    problem = user_data.get('problem')
    comment = user_data.get('comment')
    status = user_data.get('status')

    order_id = await request.add_data(name=name,
                                      phone=phone,
                                      device=device,
                                      problem=problem,
                                      status=status)

    editor = message.from_user.first_name
    await request.add_comments(order_id=order_id,
                               comment=comment,
                               editor=editor)

    await message.answer(text=f'{message.from_user.first_name}, Заказ успешно создан', reply_markup=inline_keyboard_start())

    message_group = f'{message.from_user.first_name} Создал новый заказ!\r\n' \
                    f'Заказ: <b>№{order_id}</b>\r\n' \
                    f'Имя: {name}\r\n' \
                    f'Контакты: {phone}\r\n' \
                    f'Устройство: {device}\r\n'\
                    f'Описание проблемы: {problem}\r\n' \
                    f'Статус заказа: {status}\r\n' \
                    f'Комментарий: {comment}'

    await bot.send_message(chat_id=GROUP_ID, text=message_group)
    await state.clear()



#######################################################################################################################


@router.callback_query(F.data == 'Edit')
async def get_id_to_edit(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer(f'Введи номер заказа для изменения')
    await state.set_state(EditData.GET_ID)


@router.message(StateFilter(EditData.GET_ID))
async def give_data_to_edit(message: Message, state: FSMContext, request: Request):
    await state.update_data(order_id=message.text)
    data = await state.get_data()
    order_id = data.get('order_id')
    id = await request.get_order(id=order_id)
    if id:
        await message.answer(
            f"Заказ:   <b>№{id['id']}</b> от {id['created_at']}\n"
            f"Имя:  <b>{id['name']}</b>\n"
            f"Контакты:   {id['phone']}\n"
            f"Устройство:    <b>{id['device']}</b>\n"
            f"Подтвердите изменение заказа",
            reply_markup=inline_keyboard_confirm_edit_data()
        )

        # await state.set_state(EditData.CONFIRM_EDIT)
    else:
        await message.answer(f"Заказ под таким номером не существует")



@router.callback_query(F.data == 'Confirm')
async def give_data_to_confirm_edit(call: CallbackQuery, state: FSMContext, request: Request):
    await call.answer()
    data = await state.get_data()
    order_id = data.get('order_id')
    id = await request.get_order(id=order_id)
    order_id = await request.get_comments(order_id=order_id)
    if id:
        if order_id:
            comments_text = "\n\n".join(
                f"<b>{c['editor']}</b> в <u>{c['created_at']}</u>:\n   {c['comment']}"
                for c in order_id
            )
        else:
            comments_text = "Комментариев пока нет."

        await call.message.edit_text(
            f"Заказ:   <b>№{id['id']}</b> от {id['created_at']}\n"
            f"Имя:  <b>{id['name']}</b>\n"
            f"Контакты:   {id['phone']}\n"
            f"Устройство:    <b>{id['device']}</b>\n"
            f"Описание проблемы: \n   <b>{id['problem']}</b>\n\n"
            f"Статус заказа:    <b>{id['status']}</b>\n\n"
            f"<b>Комментарии:</b>\n{comments_text}\n\n"
            f"Выберите то, что хотите изменить",
            reply_markup=inline_keyboard_edit_data()
        )

        await state.set_state(EditData.GIVE_DATA)
    else:
        await call.message.answer(f"Нужно выбрать пункт")


##################################################################################################################


#1

@router.callback_query(StateFilter(EditData.GIVE_DATA), F.data == 'Edit_name')
async def edit_name(call: CallbackQuery,  state: FSMContext):
    await call.answer()
    await call.message.answer(f'Введите новые данные:')
    await state.set_state(EditData.EDIT_NAME)


@router.message(StateFilter(EditData.EDIT_NAME))
async def confirm_edit_name(message: Message, state: FSMContext, request: Request):
    await state.update_data(edited_name=message.text)
    data = await state.get_data()
    edited_name = data.get("edited_name")
    order_id = data.get("order_id")

    await request.edit_name(name=edited_name, id=order_id)
    await message.answer(f'Данные успешно изменены!', reply_markup=inline_keyboard_start())
    await state.clear()

#2

@router.callback_query(StateFilter(EditData.GIVE_DATA), F.data == 'Edit_contact')
async def edit_phone(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer(f'Введите новые данные:')
    await state.set_state(EditData.EDIT_PHONE)


@router.message(StateFilter(EditData.EDIT_PHONE))
async def confirm_edit_phone(message: Message, state: FSMContext, request: Request):
    await state.update_data(edited_phone=message.text)
    data = await state.get_data()
    edited_phone = data.get("edited_phone")
    order_id = data.get("order_id")

    await request.edit_phone(phone=edited_phone, id=order_id)
    await message.answer(f'Данные успешно изменены!', reply_markup=inline_keyboard_start())
    await state.clear()

#3

@router.callback_query(StateFilter(EditData.GIVE_DATA), F.data == 'Edit_device')
async def edit_device(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer(f'Введите новые данные:')
    await state.set_state(EditData.EDIT_DEVICE)


@router.message(StateFilter(EditData.EDIT_DEVICE))
async def confirm_edit_device(message: Message, state: FSMContext, request: Request):
    await state.update_data(edited_device=message.text)
    data = await state.get_data()
    edited_device = data.get("edited_device")
    order_id = data.get("order_id")

    await request.edit_device(device=edited_device, id=order_id)
    await message.answer(f'Данные успешно изменены!', reply_markup=inline_keyboard_start())
    await state.clear()

#4

@router.callback_query(StateFilter(EditData.GIVE_DATA), F.data == 'Edit_problem')
async def edit_problem(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer(f'Введите новые данные:')
    await state.set_state(EditData.EDIT_PROBLEM)


@router.message(StateFilter(EditData.EDIT_PROBLEM))
async def confirm_edit_problem(message: Message, state: FSMContext, request: Request):
    await state.update_data(edited_problem=message.text)
    data = await state.get_data()
    edited_problem = data.get("edited_problem")
    order_id = data.get("order_id")

    await request.edit_problem(problem=edited_problem, id=order_id)
    await message.answer(f'Данные успешно изменены!', reply_markup=inline_keyboard_start())
    await state.clear()

#5

@router.callback_query(StateFilter(EditData.GIVE_DATA), F.data == 'Add_comments')
async def add_comment(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer(f'Введите новые данные:')
    await state.set_state(EditData.ADD_COMMENTS)


@router.message(StateFilter(EditData.ADD_COMMENTS))
async def confirm_edit_comment(message: Message, state: FSMContext, request: Request):
    await state.update_data(added_comment=message.text)
    data = await state.get_data()
    added_comment = data.get("added_comment")
    order_id = data.get("order_id")
    editor = message.from_user.first_name
    await request.add_comments(order_id=order_id, comment=added_comment, editor=editor)
    await message.answer(f'Данные успешно добавлены', reply_markup=inline_keyboard_start())
    await state.clear()


###################################################################################################################

@router.callback_query(F.data == 'Finish')
async def get_id_to_finish(call: CallbackQuery, state: FSMContext):
    await call.answer()
    f_msg = await call.message.answer(f'Введи номер заказа для изменения статуса')
    await state.update_data(first_msg_id=f_msg.message_id)
    await state.set_state(FinishOrder.GET_ID)


@router.message(StateFilter(FinishOrder.GET_ID))
async def give_data_to_finish(message: Message, state: FSMContext, request: Request):
    await state.update_data(order_id=message.text)
    data = await state.get_data()
    order_id = data.get('order_id')
    id = await request.get_order(id=order_id)
    ord_id = await request.get_comments(order_id=order_id)
    if id:
        if ord_id:
            comments_text = "\n\n".join(
                f"<b>{c['editor']}</b> в <u>{c['created_at']}</u>:\n   {c['comment']}"
                for c in ord_id
            )
        else:
            comments_text = "Комментариев пока нет."

        s_msg = await message.answer(
            f"Заказ:   <b>№{id['id']}</b> от {id['created_at']}\n"
            f"Имя:  <b>{id['name']}</b>\n"
            f"Контакты:   {id['phone']}\n"
            f"Устройство:    <b>{id['device']}</b>\n"
            f"Описание проблемы: \n   <b>{id['problem']}</b>\n\n"
            f"Статус заказа:    <b>{id['status']}</b>\n\n"
            f"<b>Комментарии:</b>\n{comments_text}\n\n"
            f"Выберите новый статус заказа",
            reply_markup=reply_keyboard_end_order()
        )
        await state.update_data(second_msg_id=s_msg.message_id)
        await state.set_state(FinishOrder.FINISH_ORDER)
    else:
        await message.answer(f"Заказ под таким номером не существует", reply_markup=inline_keyboard_start())



@router.message(StateFilter(FinishOrder.FINISH_ORDER))
async def confirm_edit_status(message: Message, bot: Bot, state: FSMContext, request: Request):
    await state.update_data(status=message.text)
    data = await state.get_data()
    status = data.get("status")
    order_id = data.get("order_id")
    f_msg_id = data.get("first_msg_id")
    s_msg_id = data.get("second_msg_id")
    await request.finish_status(status=status, id=order_id)
    await bot.delete_messages(
            chat_id=message.chat.id,
            message_ids=[f_msg_id, s_msg_id])
    await message.answer(f'Статус заказа №{order_id} изменён\nна <b>{status}</b>!', reply_markup=inline_keyboard_start())
    await state.clear()


#######################################################################################################################


@router.callback_query(F.data == 'History')
async def get_history_type(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text('Выберите метод поиска', reply_markup=inline_keyboard_history())


@router.callback_query(F.data == 'find_by_id')
async def get_history_by_id(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer(f'Введите номер заказа')
    await state.set_state(OrderHistory.ORDER_ID)

@router.message(StateFilter(OrderHistory.ORDER_ID))
async def give_data_history(message: Message, state: FSMContext, request: Request):
    await state.update_data(ord_id=message.text)
    data = await state.get_data()
    ord_id = data.get('ord_id')
    id = await request.get_order(id=ord_id)
    ord_id = await request.get_comments(order_id=ord_id)
    if id:
        if ord_id:
            comments_text = "\n\n".join(
                f"<b>{c['editor']}</b> в <u>{c['created_at']}</u>:\n   {c['comment']}"
                for c in ord_id
            )
        else:
            comments_text = "Комментариев пока нет."

        await message.answer(
            f"Заказ:   <b>№{id['id']}</b> от {id['created_at']}\n"
            f"Имя:  <b>{id['name']}</b>\n"
            f"Контакты:   {id['phone']}\n"
            f"Устройство:    <b>{id['device']}</b>\n"
            f"Описание проблемы: \n   <b>{id['problem']}</b>\n\n"
            f"Статус заказа:    <b>{id['status']}</b>\n\n"
            f"<b>Комментарии:</b>\n{comments_text}", reply_markup=inline_keyboard_find_by_back()
        )
    else:
        await message.answer(f"Заказ под таким номером не существует", reply_markup=inline_keyboard_find_by_back())
    await state.clear()


@router.callback_query(F.data == 'find_by_name')
async def get_history_by_name(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer(f'В этом формате поиска информация о заказе будет в укороченном виде. \n\nДля детальной информации используйте формат поиска по ID.\n\nВведите имя клиента')
    await state.set_state(OrderHistory.ORDER_NAME)

@router.message(StateFilter(OrderHistory.ORDER_NAME))
async def give_data_history_by_name(message: Message, state: FSMContext, request: Request):
    await state.update_data(client_name=message.text)
    data = await state.get_data()
    cl_name = data.get('client_name')
    orders = await request.get_order_by_name(name=cl_name)
    if orders:
        text = "\n\n".join(f"№<b>{o['id']}</b> от {o['created_at']}\n"
                           f"Устройство:    <b>{o['device']}</b>"
            for o in orders)
        await message.answer(f'Заказы на имя {cl_name}:\n{text}', reply_markup=inline_keyboard_find_by_id())
    else:
        await message.answer(f"Заказов зарегистрированных на это имя нет", reply_markup=inline_keyboard_find_by_back())
    await state.clear()


@router.callback_query(F.data == 'find_by_phone')
async def get_history_by_phone(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer(f'В этом формате поиска информация о заказе будет в укороченном виде. \n\nДля детальной информации используйте формат поиска по ID.\n\nВведите последние цифры мобильного телефона клиента(точность поиска зависит от количества цифр)')
    await state.set_state(OrderHistory.ORDER_PHONE)

@router.message(StateFilter(OrderHistory.ORDER_PHONE))
async def give_data_history_by_phone(message: Message, state: FSMContext, request: Request):
    await state.update_data(client_phone=message.text)
    data = await state.get_data()
    cl_phone = data.get('client_phone')
    orders = await request.get_order_by_phone(cl_phone)
    if orders:
        text = "\n\n".join(f"№<b>{o['id']}</b> от {o['created_at']}\n"
                           f"Имя клиента: {o['name']}\n"
                           f"Устройство: <b>{o['device']}</b>"
            for o in orders)
        await message.answer(f'Найденные заказы:\n{text}', reply_markup=inline_keyboard_find_by_id())
    else:
        await message.answer(f"Ничего не найдено", reply_markup=inline_keyboard_find_by_back())
    await state.clear()



#######################################################################################################################
# Добавить старый заказ

@router.callback_query(F.data == 'OldOrder')
async def old_order_get_id(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите номер старого заказа:')
    await state.set_state(AddOldOrder.GET_ID)


@router.message(StateFilter(AddOldOrder.GET_ID))
async def old_order_check_id(message: Message, state: FSMContext, request: Request):
    order_id = message.text
    if not order_id.isdigit():
        await message.answer('Номер заказа должен быть числом. Попробуйте ещё раз:')
        return
    existing = await request.get_order(id=int(order_id))
    if existing:
        await message.answer(f'Заказ с номером {order_id} уже существует. Введите другой номер:')
        return
    await state.update_data(old_order_id=int(order_id))
    await message.answer(f'Заказ <b>№{order_id}</b>\n\nВведите имя клиента:')
    await state.set_state(AddOldOrder.GET_NAME)


@router.message(StateFilter(AddOldOrder.GET_NAME))
async def old_order_get_phone(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите контактные данные клиента')
    await state.set_state(AddOldOrder.GET_PHONE)


@router.message(StateFilter(AddOldOrder.GET_PHONE))
async def old_order_get_device(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer('Введите наименование устройства')
    await state.set_state(AddOldOrder.GET_DEVICE)


@router.message(StateFilter(AddOldOrder.GET_DEVICE))
async def old_order_get_problem(message: Message, state: FSMContext):
    await state.update_data(device=message.text)
    await message.answer('Опишите проблему')
    await state.set_state(AddOldOrder.GET_PROBLEM)


@router.message(StateFilter(AddOldOrder.GET_PROBLEM))
async def old_order_get_status(message: Message, state: FSMContext):
    await state.update_data(problem=message.text)
    await message.answer('Выберите статус заказа', reply_markup=reply_keyboard_status())
    await state.set_state(AddOldOrder.GET_STATUS)


@router.message(StateFilter(AddOldOrder.GET_STATUS))
async def old_order_get_comments(message: Message, state: FSMContext):
    await state.update_data(status=message.text)
    await message.answer('Добавьте комментарий')
    await state.set_state(AddOldOrder.GET_COMMENTS)


@router.message(StateFilter(AddOldOrder.GET_COMMENTS))
async def old_order_save(message: Message, bot: Bot, state: FSMContext, request: Request):
    await state.update_data(comment=message.text)
    user_data = await state.get_data()
    order_id = user_data.get('old_order_id')
    name = user_data.get('name')
    phone = user_data.get('phone')
    device = user_data.get('device')
    problem = user_data.get('problem')
    status = user_data.get('status')
    comment = user_data.get('comment')

    await request.add_old_order(id=order_id, name=name, phone=phone, device=device, problem=problem, status=status)
    await request.sync_order_sequence()

    editor = message.from_user.first_name
    await request.add_comments(order_id=order_id, comment=comment, editor=editor)

    await message.answer(f'Старый заказ <b>№{order_id}</b> успешно добавлен!', reply_markup=inline_keyboard_start())

    message_group = f'{message.from_user.first_name} добавил старый заказ!\r\n' \
                    f'Заказ: <b>№{order_id}</b>\r\n' \
                    f'Имя: {name}\r\n' \
                    f'Контакты: {phone}\r\n' \
                    f'Устройство: {device}\r\n' \
                    f'Описание проблемы: {problem}\r\n' \
                    f'Статус заказа: {status}\r\n' \
                    f'Комментарий: {comment}'

    await bot.send_message(chat_id=GROUP_ID, text=message_group)
    await state.clear()


#########################################################################################################################################################
#########################################################################################################################################################
#########################################################################################################################################################



