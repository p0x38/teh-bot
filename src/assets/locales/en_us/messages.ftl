level-up =
    { $tone ->
        [formal] { $is_same_tier ->
            [true] { $user }, you have reached level { $level }. You remain within the { $tier } tier. Continue your steady progress.
           *[false] { $user }, congratulations. You have advanced to level { $level }, entering the { $tier } tier.
        }

        [chaotic] { $is_same_tier ->
            [true] { $user } LEVEL { $level }!!! same tier tho... still { $tier }... keep grinding gremlin 🔥
           *[false] 🚨🚨🚨 { $user } JUST BLASTED INTO LEVEL { $level } AND UNLOCKED { $tier } TIER LET'S GOOOO 🚨🚨🚨
        }

        [silly] { $is_same_tier ->
            [true] hehe { $user } is now level { $level }~ still vibing in { $tier } tier :3
           *[false] boing!! { $user } bounced into level { $level } and landed in { $tier } tier 🎉
        }

        [casual] { $is_same_tier ->
            [true] { $user } reached level { $level }. Still in { $tier } tier, keep going 👍
           *[false] nice { $user }, level { $level }! You just hit { $tier } tier 🔥
        }

       *[normal] { $is_same_tier ->
            [true] { $user } reached level { $level }. Current tier: { $tier }.
           *[false] { $user } reached level { $level } and advanced to { $tier } tier.
        }
    }