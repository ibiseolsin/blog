# AIFFEL Campus Code Peer Review Templete
- 코더 : 선다비
- 리뷰어 : 지훈

# PRT(Peer Review Template)
[O] **1. 주어진 문제를 해결하는 완성된 코드가 제출되었나요?**
- Todo 앱의 핵심 기능(할 일 추가, 완료 토글, 삭제, 마감일 설정, 태그)이 `server.py`의 GET/POST/PATCH/DELETE 라우팅과 `db.py`의 Supabase REST 연동을 통해 정상적으로 동작합니다.
- 근거: `server.py`의 `do_GET/do_POST/do_PATCH/do_DELETE`가 `/api/tasks`, `/api/tasks/<id>`를 모두 처리하고, `public/app.js`의 `loadTasks/toggleDone/deleteTask`가 이를 그대로 호출합니다. 여기에 더해 macOS 메뉴바에서 바로 쓸 수 있는 `menubar/MenuBarApp.swift` 클라이언트까지 구현되어 있어 완성도가 높습니다.

[X] **2. 핵심적이거나 복잡하고 이해하기 어려운 부분에 작성된 설명을 보고 해당 코드가 잘 이해되었나요?**
- `supabase/schema.sql` 26~30번째 줄은 예외적으로 아주 잘 설명되어 있습니다. "왜 RLS 정책을 하나도 만들지 않았는지"(개인용 앱이라 사용자 구분이 필요 없고, service_role 키만 RLS를 우회해 접근 가능하도록 default-deny로 설계했다는 의도)가 주석으로 명확히 남아 있습니다.
- 다만 이보다 더 복잡한 로직들, 예를 들어 `db.py`의 태그 다대다 관계 처리(`_get_or_create_tag_id`, `_set_task_tags`), `server.py`의 정적 파일 경로 탈출 방지 로직(`_serve_static`의 `full_path.startswith(PUBLIC_DIR)` 검사), `menubar/MenuBarApp.swift`의 서버 자동 실행 로직(`ensureServerRunning`)에는 주석이 전혀 없어서, 코드만 보고는 "왜 이렇게 짰는지"를 파악하기 어려웠습니다.

[X] **3. 에러가 난 부분을 디버깅하여 "문제를 해결한 기록"을 남겼나요? 또는 "새로운 시도 및 추가 실험"을 해봤나요?**
- 커밋이 `Add local Todo app (Python stdlib backend, Supabase-ready, menu bar client)` 하나로 스쿼시되어 있어 개발 과정의 시행착오를 커밋 히스토리에서 확인할 수 없었습니다.
- `0720_todo` 폴더 안에 별도 README나 기록 문서가 없어서, 에러를 만났고 어떻게 해결했는지, 혹은 스펙 외에 추가로 시도해본 것이 있는지 확인할 근거를 찾지 못했습니다.

[X] **4. 회고를 잘 작성했나요?**
- `0720_todo` 폴더 어디에서도 배운 점/아쉬운 점/느낀 점 등 회고에 해당하는 내용을 찾지 못했습니다.

[O] **5. 코드가 간결하고 효율적인가요?**
- `server.py`는 HTTP 메서드별로 핸들러가 분리되어 있고, `db.py`도 함수 하나당 책임이 명확해 전반적으로 중복 없이 깔끔하게 모듈화되어 있습니다.
- 근거: `db.py`의 `list_tasks/get_task/create_task/update_task/delete_task`가 각각 단일 책임으로 나뉘어 있고, `server.py`의 `_send_json/_read_json_body/_serve_static` 같은 공통 로직이 헬퍼로 분리되어 중복을 줄였습니다.
- 다만 한 가지 감점 요인이 있습니다: `menubar/MenuBarApp.swift` 35번째 줄에 `/Users/seonsuji/Desktop/hookingpoint/0720_todo/start_server.command`처럼 **작성자 개인 macOS 경로가 하드코딩**되어 있어, 다른 사람의 컴퓨터(리뷰어 포함)에서는 이 경로가 존재하지 않아 메뉴바 앱의 자동 서버 실행 기능이 그대로 깨집니다. 범용성을 위해 실행 파일 기준 상대 경로나 환경변수로 바꾸는 것을 제안합니다.

# 참고 링크 및 코드 개선
```
# 코드 리뷰 시 참고한 링크
- 없음 (정적 코드 리딩만으로 리뷰 진행)

# 제안하는 개선점
1. db.py, server.py, MenuBarApp.swift의 핵심 로직에 "왜 이렇게 짰는지" 설명하는 주석 추가
2. README 또는 커밋 메시지에 개발 중 겪은 에러/디버깅 과정, 추가로 시도해본 점 기록
3. 회고(배운 점/아쉬운 점) 섹션 추가
4. MenuBarApp.swift의 하드코딩된 절대 경로(/Users/seonsuji/...)를 상대 경로 또는 설정값으로 변경
```
