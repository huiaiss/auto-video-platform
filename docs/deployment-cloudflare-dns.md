# longjiang-ai.com Cloudflare Pages 部署 + 阿里云DNS配置方案

> 2026-06-05 | 用户已购域名 longjiang-ai.com（阿里云），DNS未配置，记录数为0
> 当前操作：阿里云DNS解析设置页面（记录数0）

---

## 一、为什么选 Cloudflare Pages？

| 维度 | Cloudflare Pages | 阿里云OSS+CDN |
|------|-----------------|---------------|
| 月费 | 免费（5GB/月） | ~30元/月 |
| HTTPS | 自动SSL | 需单独配置 |
| 全球CDN | 330+节点 | 仅国内 |
| AI爬虫友好 | ✅ 全球低延迟 | ✅ |
| 部署方式 | Git推送 / Wrangler CLI | 手动上传 |
| 备案要求 | 境外节点无需备案 | 国内节点必须备案 |

---

## 二、步骤一：注册Cloudflare + 添加域名

1. 访问 https://dash.cloudflare.com 注册
2. 点击 Add a Site → 输入 longjiang-ai.com → Free计划
3. Cloudflare扫描DNS（当前记录0，扫描结果空）
4. 继续 → 记下分配的NameServer（两个NS地址）

---

## 三、步骤二：在阿里云修改NameServer（关键！）

### 当前状态
你在阿里云DNS解析设置页面，记录数为0。

### 操作方法

| 步骤 | 操作说明 |
|------|----------|
| 1 | 阿里云控制台 → 域名 → 域名列表 |
| 2 | 点击 longjiang-ai.com 右侧「管理」 |
| 3 | 左侧菜单选「DNS修改」 |
| 4 | 点击「修改DNS服务器」 |
| 5 | 替换为Cloudflare分配的NS（如：darl.ns.cloudflare.com） |
| 6 | 确认修改，等待生效（5分钟~24小时） |

> ⚠ 改完NS后，阿里云的DNS解析设置页面将不再生效。所有DNS管理转移到Cloudflare。

### 验证命令
·þÎñÆ÷:  UnKnown
Address:  fe80::1

longjiang-ai.com	nameserver = dns18.hichina.com
longjiang-ai.com	nameserver = dns17.hichina.com

---

## 四、步骤三：Cloudflare DNS 配置

NS生效后，在Cloudflare Dashboard添加DNS记录：

| 类型 | 名称 | 值 | 代理 | 说明 |
|------|------|-----|------|------|
| CNAME | @ | long-jiang-ai-com.pages.dev | ✅ 开启 | 根域名→Pages |
| CNAME | www | long-jiang-ai-com.pages.dev | ✅ 开启 | www→Pages |

> Pages项目名 long-jiang-ai-com 是示例，以你创建时为准。

---

## 五、步骤四：部署到Cloudflare Pages

### 安装Wrangler

added 34 packages in 5s

6 packages are looking for funding
  run `npm fund` for details

 ⛅️ wrangler 4.98.0
───────────────────
Attempting to login via OAuth...
Opening a link in your default browser: https://dash.cloudflare.com/oauth2/auth?response_type=code&client_id=54d11594-84e4-41aa-b438-e81b8fa78ee7&redirect_uri=http%3A%2F%2Flocalhost%3A8976%2Foauth%2Fcallback&scope=account%3Aread%20user%3Aread%20workers%3Awrite%20workers_kv%3Awrite%20workers_routes%3Awrite%20workers_scripts%3Awrite%20workers_tail%3Aread%20d1%3Awrite%20pages%3Awrite%20zone%3Aread%20ssl_certs%3Awrite%20ai%3Awrite%20ai-search%3Awrite%20ai-search%3Arun%20websearch.run%20agent-memory%3Awrite%20queues%3Awrite%20pipelines%3Awrite%20secrets_store%3Awrite%20artifacts%3Awrite%20flagship%3Awrite%20containers%3Awrite%20cloudchamber%3Awrite%20connectivity%3Aadmin%20email_routing%3Awrite%20email_sending%3Awrite%20browser%3Awrite%20offline_access&state=UZf.lUuR-j6.E8Tu3lLutxYv.hXlOHLI&code_challenge=4Lx_h8s2LZm4Fs_jUqgOG_lfZJwriBXbkEbH5D5-RG4&code_challenge_method=S256

### 部署

 ⛅️ wrangler 4.98.0
───────────────────

### 绑定域名

wrangler pages

⚡️ Configure Cloudflare Pages

COMMANDS
  wrangler pages dev [directory] [command]  Develop your full-stack Pages application locally
  wrangler pages functions                  Helpers related to Pages Functions
  wrangler pages project                    Interact with your Pages projects
  wrangler pages deployment                 Interact with the deployments of a project
  wrangler pages deploy [directory]         Deploy a directory of static assets as a Pages deployment
  wrangler pages secret                     Generate a secret that can be referenced in a Pages project
  wrangler pages download                   Download settings from your project

GLOBAL FLAGS
      --cwd             Run as if Wrangler was started in the specified directory instead of the current working directory  [string]
      --env-file        Path to an .env file to load - can be specified multiple times - values from earlier files are overridden by values in later files  [array]
  -h, --help            Show help  [boolean]
      --install-skills  Install Cloudflare agents skills, if not already present, without asking the user for confirmation  [boolean] [default: false]
  -v, --version         Show version number  [boolean]

wrangler pages

⚡️ Configure Cloudflare Pages

COMMANDS
  wrangler pages dev [directory] [command]  Develop your full-stack Pages application locally
  wrangler pages functions                  Helpers related to Pages Functions
  wrangler pages project                    Interact with your Pages projects
  wrangler pages deployment                 Interact with the deployments of a project
  wrangler pages deploy [directory]         Deploy a directory of static assets as a Pages deployment
  wrangler pages secret                     Generate a secret that can be referenced in a Pages project
  wrangler pages download                   Download settings from your project

GLOBAL FLAGS
      --cwd             Run as if Wrangler was started in the specified directory instead of the current working directory  [string]
      --env-file        Path to an .env file to load - can be specified multiple times - values from earlier files are overridden by values in later files  [array]
  -h, --help            Show help  [boolean]
      --install-skills  Install Cloudflare agents skills, if not already present, without asking the user for confirmation  [boolean] [default: false]
  -v, --version         Show version number  [boolean]

也可以在Dashboard操作：Pages → 项目 → Custom domains → 添加域名。

### 部署目录说明



---

## 六、步骤五：验证清单

| 验证项 | URL | 预期结果 |
|--------|-----|----------|
| HTTPS | https://longjiang-ai.com | 🔒 绿色安全锁 |
| 中文首页 | https://longjiang-ai.com/ | 隆江自动化首页 |
| 英文首页 | https://longjiang-ai.com/en/ | Longjiang Auto |
| 中文产品 | https://longjiang-ai.com/products/LJ-9WD-1.html | 中文产品参数 |
| 英文产品 | https://longjiang-ai.com/en/products/LJ-9WD-1.html | English specs |
| sitemap | https://longjiang-ai.com/sitemap.xml | 双语URL列表 |
| robots | https://longjiang-ai.com/robots.txt | Allow所有 |

---

## 七、常见问题

**Q: 改完NS后多久生效？**
A: 通常5-30分钟，最长24小时。

**Q: 国内访问Cloudflare慢？**
A: Cloudflare国内节点质量尚可。如果确实慢，可等备案完成后叠加阿里云OSS。

**Q: 需要备案吗？**
A: Cloudflare境外节点不需要备案。如果用阿里云国内服务器则需要。

**Q: 修改NS后阿里云DNS页面还能用吗？**
A: 不能。DNS管理完全转移到Cloudflare。

---

## 八、速查命令

Generating English landing pages...
Found 37 pages
  OK 15KW单工位内绕绕线机.html -> 15KWSingle-StationInternal WindingWinding Machine
  OK 18内插装磁钢机.html -> 18内插装Magnet Inserter
  OK 22KW单工位内绕绕线机_蒙特纳利改装版.html -> 22KWSingle-StationInternal WindingWinding Machine
  OK 6伺服插磁钢点胶机.html -> 6Servo插磁钢Dispensing
  OK LJ-7HS-3双工位绕线机.html -> LJ-7HS-3Double-StationWinding Machine
  OK LJ-7HS双工位400中心绕线机.html -> LJ-7HSDouble-Station400中心Winding Machine
  OK LJ-7HS双工位500中心绕线机.html -> LJ-7HSDouble-Station500中心Winding Machine
  OK LJ-9WD-1.html -> LJ-9WD-1
  OK LJ-CG-DJ.html -> LJ-CG-DJ
  OK LJ-CGDJ-1.html -> LJ-CGDJ-1
  OK LJ-CGDJ-3.html -> LJ-CGDJ-3
  OK LJ-CZJ-Y01.html -> LJ-CZJ-Y01
  OK LJ-RT.html -> LJ-RT
  OK LJ-WRFC-SGW400.html -> LJ-WRFC-SGW400
  OK LJ-WX-2.html -> LJ-WX-2
  OK T型分块绕线机.html -> T型SegmentedWinding Machine
  OK V字型点胶磁钢机.html -> V字型DispensingMagnet Inserter
  OK 内嵌式插磁钢点胶机.html -> Embedded插磁钢Dispensing
  OK 单工位飞叉外绕机.html -> Single-Station飞叉Flyer Winding
  OK 单工位飞叉外绕机_标准型.html -> Single-Station飞叉Flyer Winding机 Standard
  OK 双工位分块绕线机.html -> Double-StationSegmentedWinding Machine
  OK 双工位点胶装磁钢机.html -> Double-StationDispensing装Magnet Inserter
  OK 双工位经济型绕线机.html -> Double-StationEconomyWinding Machine
  OK 双工位飞叉外绕机.html -> Double-Station飞叉Flyer Winding
  OK 双工位飞叉外绕机_华昊.html -> Double-Station飞叉Flyer Winding机
  OK 多股单工位内绕绕线机.html -> Multi-StrandSingle-StationInternal WindingWinding Machine
  OK 多股四工位内绕绕线机.html -> Multi-StrandFour-StationInternal WindingWinding Machine
  OK 插磁钢机_隆江v版.html -> 插Magnet Inserter 隆江v
  OK 插磁钢机_隆江标准型.html -> 插Magnet Inserter 隆江Standard
  OK 点胶装磁钢机_视觉定位-力华.html -> Dispensing装Magnet Inserter Vision Positioning
  OK 简易磁钢机.html -> 简易Magnet Inserter
  OK 经济型磁钢机.html -> EconomyMagnet Inserter
  OK 自动打纸机_外绕转子.html -> Automatic打纸机 Flyer WindingRotor
  OK 自动插签机.html -> AutomaticTag Inserter
  OK 表贴磁钢机.html -> Surface-MountMagnet Inserter
  OK 高速六工位内绕绕线机.html -> High-SpeedSix-StationInternal WindingWinding Machine
  OK 高速四工位绕线机.html -> High-SpeedFour-StationWinding Machine
Done! 37 pages -> D:uto-video-platform\output\landing_en
✅ sitemap.xml generated — 90 URLs → D:uto-video-platform\sitemap.xml
   固定页面: 16 个（中英文各8）
   产品落地页: 74 个（中英文各37）

 ⛅️ wrangler 4.98.0
───────────────────


wrangler pages

⚡️ Configure Cloudflare Pages

COMMANDS
  wrangler pages dev [directory] [command]  Develop your full-stack Pages application locally
  wrangler pages functions                  Helpers related to Pages Functions
  wrangler pages project                    Interact with your Pages projects
  wrangler pages deployment                 Interact with the deployments of a project
  wrangler pages deploy [directory]         Deploy a directory of static assets as a Pages deployment
  wrangler pages secret                     Generate a secret that can be referenced in a Pages project
  wrangler pages download                   Download settings from your project

GLOBAL FLAGS
      --cwd             Run as if Wrangler was started in the specified directory instead of the current working directory  [string]
      --env-file        Path to an .env file to load - can be specified multiple times - values from earlier files are overridden by values in later files  [array]
  -h, --help            Show help  [boolean]
      --install-skills  Install Cloudflare agents skills, if not already present, without asking the user for confirmation  [boolean] [default: false]
  -v, --version         Show version number  [boolean]

 ⛅️ wrangler 4.98.0
───────────────────
