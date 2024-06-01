import disnake
import os
from disnake.ext import commands
from disnake.ext.commands import check

# Проверка на allowed users
def load_allowed_users_from_file():
    with open("allowed_users.txt", "r") as file:
        allowed_users = [int(line.strip()) for line in file]

def is_allowed_user():
    async def predicate(interaction: disnake.ApplicationCommandInteraction):
        with open("allowed_users.txt", "r") as file:
            allowed_users = [int(line.strip()) for line in file]
        return interaction.author.id in allowed_users

    return check(predicate)

intents = disnake.Intents.default()
intents.members = True

read_data = {}
with open('datatest.txt', 'r') as file:
    for line in file:
        if ':' in line:
            key, value = line.strip().split(': ', 1)
            read_data[key] = value



class Applicationfamily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Заявка с кнопкой
    @commands.slash_command(name="app_family")
    @is_allowed_user()
    async def app_family(self, ctx):  
        embed = disnake.Embed(title="Заявка на вступления в семью", color=0x888888)
        embed.add_field(name="", value="Если у тебя появилось желание пополнить наши ряды, ты можешь оставить заявку нажав на кнопку `Создать заявку`", inline=False)  
        embed.add_field(name="Прежде чем приступить к созданию заявки, ознакомьтесь с требованиями:", value=""
                                            "```— Возраст 16+\n"
                                            "— Уровень стрельбы и понимаия игры выше среднего\n"
                                            "— Скриншот персонажей, на скриншоте должны быть видны все три персонажа.\n"
                                            "— Два отката с игры GunGame, продолжительностью 2 минуты. В первом откате оружие «Сайга», во втором — «Карабинка».```", inline=False)
        embed.set_footer(text="Famq Screamz")
     
        view = disnake.ui.View(timeout=None) 
        button = disnake.ui.Button(label="Создать заявку", style= disnake.ButtonStyle.blurple , custom_id="my_button")
        button.callback = application_callback
        view.add_item(button)

        await ctx.response.send_message(embed=embed, view=view)

# Вызов Application по нажатию на кнопки
async def application_callback(interaction: disnake.Interaction):
    modal = Application()
    await interaction.response.send_modal(modal)


# Чтения последнего номера ветки (Создания ветки)
def read_last_thread_number():
    if os.path.exists("last_thread_number.txt"):
        with open("last_thread_number.txt", "r") as file:
            return int(file.read().strip())
    else:
        return 0

# Записи нового номера ветки (Создания ветки)
def write_new_thread_number(number):
    with open("last_thread_number.txt", "w") as file:
        file.write(str(number))

# Создания ветки
async def create_thread(guild: disnake.Guild, name: str, category: disnake.CategoryChannel,
                                  inviter: disnake.Member, inter: disnake.ModalInteraction):
    last_number = read_last_thread_number()
    new_thread_number = last_number + 1
    write_new_thread_number(new_thread_number)
    
    thread_name = f"Обращение #{new_thread_number} - User id: {inter.author.id}"
    thread = await category.create_thread(name=thread_name, type=disnake.ChannelType.private_thread)
    await thread.add_user(inviter)
    return thread

# Модельное окно
class Application(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="ИМЯ И ФАМИЛИЯ",
                placeholder="Sinra Screamz",
                custom_id="0",
                max_length=30),

            disnake.ui.TextInput(
                label="OOС Возраст",
                placeholder="Ведите реальный OOC возраст",
                custom_id="1",
                max_length=15),

            disnake.ui.TextInput(
                label="СРЕДНИЙ ОНЛАЙН В ДЕНЬ:",
                placeholder="5 часов стабильно",
                custom_id="2",
                max_length=30),

            disnake.ui.TextInput(
                label="Скрин персонажей и откаты (Las Vegas)",
                placeholder="Ссылка на imgur: Персонажи \nСсылка на YouTube: Откаты",
                custom_id="3",
                max_length=200,
                style=disnake.TextInputStyle.paragraph),

            disnake.ui.TextInput(
                label="КОММЕНТАРИЙ",
                placeholder="Почему вы выбрали нашу семью и где ранее состояли?",
                custom_id="4",
                max_length=500,
                style=disnake.TextInputStyle.paragraph),
        ]

        super().__init__(title="Screamz Famq", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        guild = inter.guild
        category = guild.get_channel(int(read_data["create_thread_family"])) # id канала для веток family
        private_channel = await create_thread(guild, inter.author.name, category, inter.author, inter)

        embed = disnake.Embed(title=f"Заявка на модерацию", color=0x54D3BF)

        embed.add_field(name="", value=f"**Ник:  **{inter.text_values.get("0")[:1024]}", inline=False)
        embed.add_field(name="", value=f"**Возраст:  **{inter.text_values.get("1")[:1024]}", inline=False)
        embed.add_field(name="", value=f"**Онлайн:  **{inter.text_values.get("2")[:1024]}", inline=False)
        embed.add_field(name="Ссылки:", value=f"{inter.text_values.get("3")[:1024]}", inline=False)
        embed.add_field(name="Комментарий:", value=f"```{inter.text_values.get("4")[:1024]}```", inline=False)
        embed.add_field(name="", value=f"Заявитель: <@{inter.author.id}>", inline=False)

        embed.set_footer(text=f"Заявка от {inter.author} • User id: {inter.author.id}", icon_url=inter.author.display_avatar.url)
        embed.timestamp = inter.created_at

        view = disnake.ui.View(timeout=None)
        button = disnake.ui.Button(label="Принять", style=disnake.ButtonStyle.green, custom_id="hide_thread")
        button.callback = hide_thread_callback

        button_deny = disnake.ui.Button(label="Отклонить", style=disnake.ButtonStyle.red, custom_id="deny_thread")
        button_deny.callback = deny_thread_callback
        view.add_item(button)
        view.add_item(button_deny)

        await private_channel.send(read_data["send_role_id_thread_family"], embed=embed, view=view) # id роли инвайт в ветку

        await inter.response.send_message("Ваша заявка отправлена на рассмотрение.", ephemeral=True)

        await give_role_callback(inter)

async def _scheduled_task(self, interaction: disnake.ModalInteraction):
        channel_name = interaction.channel.name
        await self.give_role_callback(interaction, channel_name) 

async def give_role_callback(inter: disnake.ModalInteraction):
    role_id = (int(read_data["give_role_unmute"]))
    user_id = inter.user.id

    user = await inter.guild.fetch_member(user_id)  # Получаем объект пользователя
    role = inter.guild.get_role(role_id)  # Получаем объект роли

    await user.add_roles(role)  # Назначаем роль пользователю


async def _scheduled_task(self, interaction: disnake.ModalInteraction):
        channel_name = interaction.channel.name
        await self.hide_thread_callback(interaction, channel_name) 

# Кнопка "Принять" и его подзадачи
async def hide_thread_callback(inter: disnake.ModalInteraction):
    allowed_roles = [1087033118168461416, 1087033221495136327, 1223688399991607487, 1182398018461380719, 1219310981176365076, 1091809410466205897]  # Список разрешенных ролей
    user_roles = [role.id for role in inter.user.roles]
    
    if any(role_id in allowed_roles for role_id in user_roles):

        channel_name = inter.channel.name
        user = await inter.guild.fetch_member(f"{channel_name.split("User id:")[1]}")

        # Удаления роли unmute
        role_id_to_remove = (int(read_data["give_role_unmute"]))
        role_to_remove = disnake.utils.get(user.guild.roles, id=role_id_to_remove)
        await user.remove_roles(role_to_remove)

        await user.send(f"Ваше обращение №{channel_name.split("#")[1].split(" ")[0]} одобрено!\n"
                        f"Возникли вопросы? обратитесь, пожалуйста, к модератору: {inter.author.mention}\n")

        log_embed = disnake.Embed(title="Заявка принята", description=f"Модератор: **{inter.user.name}**  {inter.user.mention}\n"
                                                                                f"Заявитель: NaN\n"
                                                                                f"Ветка: {inter.channel.mention}\n", color=0x20BA6F)
        log_embed.set_thumbnail(url=inter.user.avatar)
        log_embed.set_footer(text=f"User id: {inter.author.id}", icon_url=inter.author.display_avatar.url)
        log_embed.timestamp = inter.created_at
        

        await inter.response.send_message(f"Заявка принята модератором: {inter.user.mention}")
        await inter.channel.edit(archived=True)

        log_channel_id = int(read_data["log_channel_id_def"])
        log_channel = inter.guild.get_channel(log_channel_id)
        await log_channel.send(embed=log_embed)
    else:
        await inter.response.send_message("У вас нет права принимать заявки.", ephemeral=True)


# Кнопка "Откланить" и его подзадачи
async def deny_thread_callback(interaction: disnake.Interaction):
    allowed_roles = [1087033118168461416, 1087033221495136327, 1223688399991607487, 1182398018461380719, 1219310981176365076, 1091809410466205897]  # Список разрешенных ролей
    user_roles = [role.id for role in interaction.user.roles]
    
    if any(role_id in allowed_roles for role_id in user_roles):
        modal1013 = DenyModal()
        await interaction.response.send_modal(modal1013)
    else:
        await interaction.response.send_message("У вас нет права отклонять заявки.", ephemeral=True)


class DenyModal(disnake.ui.Modal):
    def __init__(self):

        components = [
            disnake.ui.TextInput(
                label="Причина отказа",
                placeholder="Введите причину отказа",
                custom_id="deny_reason",
                max_length=400,
                style=disnake.TextInputStyle.paragraph),

        ]

        super().__init__(title="Screamz Famq", components=components)


    async def _scheduled_task(self, interaction: disnake.ModalInteraction):
        channel_name = interaction.channel.name
        await self.callback(interaction, channel_name) 

    async def callback(self, inter: disnake.ModalInteraction, channel_name: str):

        user = await inter.guild.fetch_member(f"{channel_name.split("User id:")[1]}")

        # Удаления роли unmute
        role_id_to_remove = (int(read_data["give_role_unmute"]))
        role_to_remove = disnake.utils.get(user.guild.roles, id=role_id_to_remove)
        await user.remove_roles(role_to_remove)

        await user.send(f"Ваше обращение №{channel_name.split("#")[1].split(" ")[0]} отказано!\n"
                        f"Причина: {inter.text_values.get("deny_reason")[:1024]}\n")

        logs_embed = disnake.Embed(title="Заявка отклонена", description=f"Модератор: **{inter.user.name}**  {inter.user.mention}\n"
                                                                                f"Заявитель(id): {channel_name.split("User id:")[1]}\n"
                                                                                f"Ветка: {inter.channel.mention}\n"
                                                                                f"Причина отказа:\n```{inter.text_values.get("deny_reason")[:1024]}```", color=0xEA5454)
        logs_embed.set_thumbnail(url=inter.user.avatar)
        logs_embed.set_footer(text=f"User id: {inter.author.id}", icon_url=inter.author.display_avatar.url)
        logs_embed.timestamp = inter.created_at
        
        await inter.response.send_message(f"Заявку отклонил модератор: {inter.user.mention}")
        await inter.channel.edit(archived=True)

        logs_channel_id = int(read_data["log_channel_id_def"]) # id канала для логов
        logs_channel = inter.guild.get_channel(logs_channel_id)
        await logs_channel.send(embed=logs_embed)


def setup(bot):
    bot.add_cog(Applicationfamily(bot))