import discord
from discord.ext import commands
from discord.ui import Button, View

from datetime import datetime
import config

from datetime import timedelta

intents = discord.Intents().all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await update(None)
    print(f'We have logged in as {bot.user}')

@bot.command()
@commands.has_permissions(administrator=True)
async def update(ctx):

    target_channels = [1249791959027941418,1244421754676445336] # ID of the target channel
    command_channel = {1249791959027941418:'redan',
                       1244421754676445336:'fam'
                       }
    for i in target_channels:
        target_channel = bot.get_channel(i)
        await target_channel.purge()
        message = await target_channel.send('Updating ...', delete_after = 10)
        context = await bot.get_context(message)
        await context.invoke(bot.get_command(command_channel[i]))
    print('Successfully updated')


class Feedback(discord.ui.Modal, title='Feedback'):
    
    name = discord.ui.TextInput(
        label='Ваш NickName , staticID',
        placeholder='Dino Dinozavrov 131244',
        required=True
    )
    
    online = discord.ui.TextInput(
        label='Ваш средний онлайн',
        placeholder='7+ часов',
        required=True
    )

    levl = discord.ui.TextInput(
        label='Ваш Уровень персонажа',
        placeholder='8',
        required=True
    )
    
    ask = discord.ui.TextInput(
        label='Чем планируете заниматься?',
        placeholder='Хочу Жоско любить и радовать Кота',
        required=True
    )

    asked = discord.ui.TextInput(
        label='Почему решили вступить?',
        style=discord.TextStyle.long,
        placeholder='Хочу помогать Любимому Котовскому',
        required=True,
        max_length=300,
    )

    async def on_submit(self, interaction: discord.Interaction):
       
        embed = discord.Embed(
        title=f'Заявка от : {interaction.user.name}',
        color=discord.Color.blue()
    )
        
        embed.add_field(name='NickName и staticID', value=f"{self.name.value}", inline=False)
        embed.add_field(name='Cредний онлайн', value=f"{self.online.value}", inline=False)
        embed.add_field(name='Уровень Персонажа', value=f"{self.levl.value}", inline=False)
        embed.add_field(name='Почему хочет вступить и чем планирует заниматься', value=f"{self.asked.value}", inline=False)
        embed.add_field(name='Чем планирует заниматься данный кандидат', value=f"{self.ask.value}", inline=False)

        embed.set_footer(text=f"{interaction.user.id}")
        
        channel = bot.get_channel(1244396658125574245)
        v = View()
        button_accept = Button(label="Одобрить", style=discord.ButtonStyle.green)
        button_accept.callback = accept_callback
        
        button_deny = Button(label="Отклонить", style=discord.ButtonStyle.red)
        button_deny.callback = deny_callback

        v.add_item(button_accept)
        v.add_item(button_deny)
        
        await channel.send(content=f'<@&1244738466424819742>',embed=embed, view=v)
        
        await interaction.response.send_message(f'Вы успешно отправили заявку!', ephemeral=True, delete_after = 30)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)


async def accept_callback(interaction: discord.Interaction):
    message = interaction.message  
    if message.embeds:
        embed = message.embeds[0]
    user_id = embed.footer.text

    guild = interaction.guild
    member = guild.get_member(int(user_id))
    role = guild.get_role(1244419670547632178)
    await member.add_roles(role)
    
    chanel = guild.get_channel(1244422365660577893)
    await chanel.send(f'<@{user_id}>, {config.GiveRoleDone}')
    await disable_embed(message,True,interaction.user.name)

async def deny_callback(interaction: discord.Interaction):
    message = interaction.message  
    
    if message.embeds:
        embed = message.embeds[0]
        
    user_id = embed.footer.text
    guild = interaction.guild
    
    
    await interaction.response.send_modal(DenyAplication(user_id=int(user_id),message=interaction.message.id))
    await disable_embed(message,False,interaction.user.name)

class DenyAplication(discord.ui.Modal, title = "DenyAplication"):
    
    def __init__(self, user_id: int, message: int):
        super().__init__(timeout=None)  # Передача timeout=None, чтобы модальное окно не закрывалось автоматически
        self.user_id = user_id 
        self.message = message
        
        self.reason = discord.ui.TextInput(
            label='Укажите причину отказа',
            style=discord.TextStyle.long,
            placeholder='Не справился ...',
            required=False,
            max_length=300,
        )
        
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = guild.get_member(self.user_id) 
        if self.reason.value is not None:
            await member.send(f'Добрый день, к сожалению вы получили отказ на принятия в FamQ \n Причина: {self.reason.value}')
        else:
            await member.send(f'Добрый день, к сожалению вы получили отказ на принятия в FamQ \n Причина: не указана')
        await interaction.response.send_message(f'Вы успешно откланили заявку!', ephemeral=True, delete_after = 30)
        

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
		

@bot.command()
async def fam(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title="Заявка на вступления в семью", description="This is Kotov FAMQ")
    embed.add_field(name="", value="Если у тебя появилось желание пополнить наши ряды, ты можешь оставить заявку нажав на кнопку `Создать заявку`", inline=False)  
    embed.add_field(name="Прежде чем приступить к созданию заявки, ознакомьтесь с требованиями:", value=""
                                            "```— Возраст 16+\n"
                                            "— Иметь хороший средний онлайн \n"
                                            "— Желание помогать и развиватся семье ```", inline=False)
    embed.set_footer(text="Famq")
    button = Button(label="Отправить Заявку 📨", style=discord.ButtonStyle.green)


    button.callback = btn_callback
    v = View(timeout=None).add_item(button)
    await ctx.send(embed=embed,view=v)
    
async def btn_callback(interaction: discord.Interaction):
    await interaction.response.send_modal(Feedback())


@bot.event
async def on_member_join(member):
    if role := member.guild.get_role(1244419670732181636):
        await member.add_roles(role)
    

@bot.command(name='timeout')
@commands.has_permissions(moderate_members=True)  # Проверяем, что у вызывающего есть права на управление участниками
async def timeout(ctx, member: discord.Member, time: int, *, reason: str):
    await ctx.message.delete()
    if member == ctx.author:
        return await ctx.send("Вы не можете замутить самого себя", delete_after=10)

    if time < 1:
        return await ctx.send("Вы не можете замутить пользователя на меньше 1 минуты", delete_after=10)

    end_time = datetime.now().astimezone() + timedelta(minutes=time)

    await member.timeout(end_time)
    
    formatted_time = discord.utils.format_dt(end_time, style="R")
    embed = discord.Embed(
        title="Таймаут",
        description=f"Пользователь {member.mention} был затайм-аутен. Причина: {reason}. "
                    f"Таймаут будет снят {formatted_time}",
        color=0x2F3136
    ).set_thumbnail(url=member.display_avatar.url)
    
    await ctx.send(embed=embed, delete_after=60)

@bot.command(name='un_timeout')
@commands.has_permissions(moderate_members=True)  
async def un_timeout(ctx, member: discord.Member):
    await ctx.message.delete()
    await member.timeout(None)
    await ctx.send(f"Таймаут с пользователя {member.mention} был снят", delete_after=10)

@bot.command(name='clear')
@commands.has_permissions(moderate_members=True)  
async def clear(ctx, amount: int):

    await ctx.message.delete()
    await ctx.channel.purge(limit=amount)


@bot.command(name='redan')
@commands.has_permissions(moderate_members=True)  
async def redan(ctx):

    await ctx.message.delete()

    embed = discord.Embed(
        title=f'Амнистия',
        color=discord.Color.green(),
        description='Здесь вы можете подать амнистию!'
    )

    v = View()

    button = Button(label="Запросить Амнистию 👹", style=discord.ButtonStyle.red)

    button.callback = btn_callback_rdn

    v.add_item(button)

    await ctx.send(embed=embed,view=v)

async def btn_callback_rdn(interaction: discord.Interaction):
    await interaction.response.send_modal(Redan())


class Redan(discord.ui.Modal, title='Redan'):
    
    noname = discord.ui.TextInput(
        label='Ваш NickName , staticID',
        placeholder='Dino Dinozavrov 131244',
        required=True
    )
    
    ireason = discord.ui.TextInput(
        label='За что вы получили наказание?',
        placeholder='Я обидел dinozavra',
        required=True
    )

    asket = discord.ui.TextInput(
        label='Ваш коментарий',
        style=discord.TextStyle.long,
        placeholder='Стою на колени и больше так не буду',
        required=True,
        max_length=300,
    )

    async def on_submit(self, interaction: discord.Interaction):
       
        embed = discord.Embed(
        title=f'Амнистия от : {interaction.user.name}',
        color=discord.Color.red()
    )
        
        embed.add_field(name='NickName и staticID', value=f"{self.noname.value}", inline=False)
        embed.add_field(name='Причина наказания', value=f"{self.ireason.value}", inline=False)
        embed.add_field(name='Его комментарий по ситуации', value=f"{self.asket.value}", inline=False)
        

        embed.set_footer(text=f"{interaction.user.id}")
        
        channel = bot.get_channel(1244396658125574245)
        v = View()

        button_accept = Button(label="Одобрить", style=discord.ButtonStyle.green)
        button_accept.callback = redan_callbacl_acpt
        
        button_deny = Button(label="Отклонить", style=discord.ButtonStyle.red)
        button_deny.callback = redan_callbacl_deny

        v.add_item(button_accept)
        v.add_item(button_deny)
        
        await channel.send(content=f'',embed=embed, view=v) # <@378950627260104704>
        
        await interaction.response.send_message(f'Вы успешно попросили прощения, ожидайте результата!', ephemeral=True, delete_after = 30)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Ну пиздец, сам не ебу что за проблема', ephemeral=True)

async def redan_callbacl_acpt(interaction: discord.Interaction):
    message = interaction.message  
    guild = interaction.guild
    if message.embeds:
        embed = message.embeds[0]
    user_id = int(embed.footer.text)

    role = guild.get_role(1249791222122545296) # роль НАказан
    user = guild.get_member(user_id)

    role_member = guild.get_role(1244419670732181636)
    role_staf = guild.get_role(1244419670547632178)

    await user.remove_roles(role)
    await user.add_roles(role_member)
    await user.add_roles(role_staf)
    await disable_embed(message,True,interaction.user.name)

async def redan_callbacl_deny(interaction: discord.Interaction):
    message = interaction.message  
    guild = interaction.guild
    if message.embeds:
        embed = message.embeds[0]
    user_id = int(embed.footer.text)
    member = guild.get_member(user_id)
    
    await disable_embed(message,False,interaction.user.name)
    await member.send('Вам было отказано в амнистии!')


@bot.command(name='kick')
@commands.has_permissions(moderate_members=True)  
async def kick(ctx, member: discord.Member):
    await ctx.message.delete()
    guild = ctx.guild
    role_banned = guild.get_role(1249791222122545296)
    for role in member.roles:
        if role != ctx.guild.default_role:
            await member.remove_roles(role)
    await member.add_roles(role_banned)


async def disable_embed(message: discord.Message, status, user):
    # Проверяем, есть ли в сообщении embed
    if not message.embeds:
        raise ValueError("Сообщение не содержит embed.")
    
    # Извлекаем первый embed из сообщения (предполагаем, что в сообщении один embed)
    old_embed = message.embeds[0]
    
    # Создаем новый embed с теми же данными, но с измененным цветом на серый
    new_embed = discord.Embed(
        title=old_embed.title,
        description=old_embed.description,
        color=discord.Color.darker_gray()  # Используем встроенный серый цвет Discord
    )
    
    # Копируем все поля из старого embed в новый
    for field in old_embed.fields:
        new_embed.add_field(name=field.name, value=field.value, inline=field.inline)
    
    if status:
        new_embed.set_footer(text=f'✔️ by {user}')
    else:
        new_embed.set_footer(text=f'❌ by {user}') 
    
    
    # Обновляем сообщение: убираем view и заменяем embed на новый
    await message.edit(embed=new_embed, view=None)


bot.run('')