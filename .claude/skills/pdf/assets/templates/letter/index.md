---
title: {{TITLE}}
date: {{DATE}}
preset: letter
theme: light          # light | dark | both — ask the user
head: false          # a letter lays down its own heading, not a title banner
---

<div class="letterhead" markdown="1">
<div>**{{AUTHOR}}**</div>
<address>
Sender's address<br>
Postcode Town
</address>
</div>

<div class="recipient" markdown="1">
Recipient<br>
Address<br>
Postcode Town
</div>

<p class="subject">Subject: {{TITLE}}</p>

Dear Sir or Madam,

The body of the letter.

<div class="signature" markdown="1">
Yours sincerely,
**{{AUTHOR}}**
</div>
