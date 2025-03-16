from interactions import ChannelHistory, Extension
import os, time


class Citations(Extension):
    def __init__(self, bot):
        # do some initialization here
        self.zitate_channel = 844336088175607818


    async def async_start(self):
        print("trying to extract channel")
        chan = await self.bot.fetch_channel(self.zitate_channel)
        chanhist = ChannelHistory(chan, limit=50, before=None)
        messages = await chanhist.fetch()
        i=1
        with open('./db/messages.txt', 'w', encoding='utf-8') as f:
            for message in messages:
                f.write(f"{message.author.global_name} ; {message.timestamp} ; {message.content}\n")
        while True:
            i += 1
            if i % 20 == 0:
                print(f"Extracted {i * 50 * 20} messages")
            try:
                time.sleep(0.7) # to avoid the rate limit
                chanhist = ChannelHistory(chan, limit=50, before=messages[-1].id)
                messages = await chanhist.fetch()
                with open('./db/messages.txt', 'a', encoding='utf-8') as f:
                    for message in messages:
                        f.write(f"{message.author.global_name} ; {message.timestamp} ; {message.content}\n")
                if len(messages) < 50: # 1/50 chance to get fucked
                    break
            except:
                break
        print("done extracting channel")
        
            