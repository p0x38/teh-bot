level-up =
    { $tone ->
        [formal] { $is_same_tier ->
            [true] { $user }さん、レベル{ $level }に到達しました。現在も{ $tier }ティアに属しています。引き続き努力を続けてください。
           *[false] { $user }さん、おめでとうございます。レベル{ $level }に到達し、{ $tier }ティアへ昇格しました。
        }

        [chaotic] { $is_same_tier ->
            [true] { $user } レベル{ $level }！？まだ{ $tier }ティアかよｗｗ もっと暴れろ🔥
           *[false] 🚨 { $user } レベル{ $level }突破！！！{ $tier }ティア解放！！！やばすぎ 🚨
        }

        [silly] { $is_same_tier ->
            [true] { $user }はレベル{ $level }になったよ〜 まだ{ $tier }ティアだね :3
           *[false] ぴょん！{ $user }はレベル{ $level }になって{ $tier }ティアにジャンプしたよ〜 🎉
        }

        [casual] { $is_same_tier ->
            [true] { $user }、レベル{ $level }になったよ。まだ{ $tier }ティアだね 👍
           *[false] ナイス！{ $user }、レベル{ $level }！{ $tier }ティアに到達 🔥
        }

       *[normal] { $is_same_tier ->
            [true] { $user }はレベル{ $level }に到達しました。現在のティアは{ $tier }です。
           *[false] { $user }はレベル{ $level }に到達し、{ $tier }ティアに昇格しました。
        }
    }