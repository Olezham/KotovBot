import discord
from discord.ext import commands
from discord.ui import Button, View

import config

intents = discord.Intents().all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

class Feedback(discord.ui.Modal, title='Feedback'):
    
    name = discord.ui.TextInput(
        label='Ваш NickName , staticID',
        placeholder='Dino Dinozavrov 131244',
        required=True
    )
    
    # static = discord.ui.TextInput(
    #     label='Ваш ',
    #     placeholder='8',
    #     required=True
    # )
    
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
        title=f'Заявка от пользователя: {interaction.user.name}',
        color=discord.Color.brand_green()
    )
        
        embed.add_field(name='NickName и staticID', value=f"{self.name.value}", inline=False)
        # embed.add_field(name='StaticID', value=f"{self.static.value}", inline=False)
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

async def deny_callback(interaction: discord.Interaction):
    message = interaction.message  
    
    if message.embeds:
        embed = message.embeds[0]
        
    user_id = embed.footer.text
    guild = interaction.guild
    member = guild.get_member(int(user_id))
    role = guild.get_role(1244419670547632178)
    
    await interaction.response.send_modal(DenyAplication(user_id=int(user_id),message=interaction.message.id))
    
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
    
bot.run('')