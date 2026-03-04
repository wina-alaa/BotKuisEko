import discord
from discord.ext import commands
import json
import random
from config import TOKEN, DATA_FILE, QUIZ_FILE

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================== LOAD QUIZ ==================
with open("quiz.json", "r", encoding="utf-8") as f:
    quiz_data = json.load(f)

# ================== LOAD / SAVE POINTS ==================
DATA_FILE = "data.json"

try:
    with open(DATA_FILE, "r") as f:
        user_points = json.load(f)
        user_points = {int(k): v for k, v in user_points.items()}
except FileNotFoundError:
    user_points = {}

def save_points():
    with open(DATA_FILE, "w") as f:
        json.dump(user_points, f)


# ================== QUIZ VIEW ==================
class QuizView(discord.ui.View):
    def __init__(self, ctx, level, question_data):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.level = level
        self.question_data = question_data
        self.correct_answer = question_data["answer"]
        self.message = None

        # Tombol hanya A/B/C/D
        for key in question_data["options"].keys():
            self.add_item(AnswerButton(label=key, key=key))

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.ctx.author


class AnswerButton(discord.ui.Button):
    def __init__(self, label, key):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.key = key

    async def callback(self, interaction: discord.Interaction):
        view: QuizView = self.view

        if self.key == view.correct_answer:
            reward = quiz_data[view.level]["reward"]
            user_points[interaction.user.id] = user_points.get(interaction.user.id, 0) + reward
            save_points()

            await interaction.response.send_message(
                f"✅ Jawaban benar! Kamu mendapat {reward} poin.\n"
                f"Total poin kamu: {user_points[interaction.user.id]}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ Jawaban salah! Jawaban yang benar adalah {view.correct_answer}.",
                ephemeral=True
            )

        view.stop()

        # Hapus soal setelah dijawab
        if view.message:
            await view.message.delete()


# ================== COMMAND QUIZ ==================
@bot.command()
async def quiz(ctx, level: str):
    level = level.lower()

    if level not in quiz_data:
        await ctx.send("Level tidak ditemukan! Gunakan: mudah / sedang / sulit")
        return

    question_data = random.choice(quiz_data[level]["quiz_list"])

    options_text = "\n".join(
        [f"{key}. {value}" for key, value in question_data["options"].items()]
    )

    embed = discord.Embed(
        title=f"Quiz Level {level.capitalize()}",
        description=f"{question_data['question']}\n\n{options_text}",
        color=discord.Color.blue()
    )

    view = QuizView(ctx, level, question_data)
    message = await ctx.send(embed=embed, view=view)
    view.message = message


# ================== COMMAND POIN ==================
@bot.command()
async def poin(ctx):
    total = user_points.get(ctx.author.id, 0)
    await ctx.send(f"🏆 Total poin kamu: {total}")


# ================== COMMAND HELP ==================
@bot.command()
async def helpquiz(ctx, level: str):
    level = level.lower()

    if level not in quiz_data:
        await ctx.send("Level tidak ditemukan!")
        return

    materi = "\n".join(quiz_data[level]["help_quiz"])

    embed = discord.Embed(
        title=f"Materi Quiz Level {level.capitalize()}",
        description=materi,
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print(f"Bot login sebagai {bot.user}")


bot.run(TOKEN)
