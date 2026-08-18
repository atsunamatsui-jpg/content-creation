<!--
IN-PLATFORM CAMPAIGN APPLICATION
For the free-text box on Aspire / Collabstr / TikTok Creator Marketplace / etc.

These boxes are usually 500–1500 characters and get skimmed in ~10 seconds by
someone reviewing 200 applications. So: specific hook first, proof second,
logistics third. No "I'm a huge fan of your brand" opener — everyone writes it
and it signals nothing.

Render:
  python3 scripts/render_pitch.py templates/campaign-application.md \
    --set brand="BRAND" --set campaign="CAMPAIGN NAME" \
    --set hook="ONE TRUE SPECIFIC SENTENCE ABOUT THE PRODUCT" \
    --set angle="THE CONTENT IDEA" --set deliverables="1x TikTok + 2x Stories"
-->

Hi {{brand}} team,

{{hook}}

I'm {{creator.name}} ({{creator.handle}}) — {{creator.one_liner}} My audience is {{audience.top_countries}}, mostly {{audience.age_range}}, which lines up with who {{campaign}} is aimed at.

**My idea for this campaign:** {{angle}}

Why me specifically: {{creator.differentiator}}

Recent proof — {{top_content.0.url}} did {{top_content.0.result}}. {{top_content.0.why}}

**Deliverables I'm proposing:** {{deliverables}}
**Turnaround:** {{terms.turnaround}}
**Usage:** {{terms.usage_rights}}

Happy to adjust the concept to your brief. Full portfolio: {{channels.instagram.url}}

{{creator.name}}
{{creator.email}}
